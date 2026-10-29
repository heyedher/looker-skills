# PDT, Materialization, & Cold-Start Optimization Manual

This handbook defines the standards for evaluating, partitioning, clustering, and safely bootstrapping Persistent Derived Tables (PDTs) and Incremental PDTs in Looker. *(For simple Explore summary rollups that do not require custom SQL joins or window functions, prefer Looker native `aggregate_table` blocks before creating custom SQL PDTs.)*

---

## 1. The 4-Quadrant PDT Decision Matrix

Do **NOT** materialize simple 1:1 raw tables as PDTs. Every PDT adds warehouse storage and build-time compute cost. Evaluate all four quadrants first:

| Quadrant | Materialize as PDT | Keep as Live Explore Query |
| :--- | :--- | :--- |
| **1. Query Complexity** | Heavy regex, window functions, or multi-stage joins (`> 10s` runtime) | Simple predicates, aggregates, and indexed joins (`< 3s` runtime) |
| **2. Query Concurrency** | High-traffic executive dashboards queried hundreds of times daily | Sporadic ad-hoc exploration by analysts |
| **3. Freshness SLA** | Hourly, daily, or batch-ETL latency acceptable | Sub-minute / real-time operational freshness required |
| **4. Source Scale** | Massive (`> 50M` rows) or unpartitioned source tables | Compact (`< 10M` rows), partitioned/indexed tables |

---

## 2. Dialect-Specific Physical Optimization Standards

Materialized PDTs **MUST** declare physical partitioning, clustering, or DDL indexes matching Looker's LookML compiler grammar:

### A. Google Cloud BigQuery (`partition_keys` & `cluster_keys`)
Use LookML's array parameters `partition_keys` (single date/timestamp column) and `cluster_keys` (up to 4 high-selectivity filter/join columns, ordered highest to lowest cardinality) -- never dbt's `partition_by` or `cluster_by`:

```lookml
view: pdt_order_rollup {
  derived_table: {
    sql:
      SELECT order_date, user_id, status, SUM(sale_price) AS revenue_total
      FROM @{DATASET_NAME}.order_items
      GROUP BY 1, 2, 3 ;;
    datagroup_trigger: daily_etl_datagroup
    partition_keys: ["order_date"]
    cluster_keys: ["user_id", "status"]
  }
}
```

### B. Google Cloud Spanner (`create_process` with Primary Key & Secondary Indexes)
Cloud Spanner requires explicit `PRIMARY KEY` DDL. Because `derived_table.sql` wraps a `SELECT` statement, multi-step Spanner DDL (`CREATE TABLE` + `CREATE INDEX` + `INSERT`) **MUST** use `create_process` with `${SQL_TABLE_NAME}` and `--` SQL comments:

```lookml
view: pdt_user_orders_summary {
  derived_table: {
    datagroup_trigger: daily_etl_datagroup
    create_process: {
      sql_step:
        CREATE TABLE ${SQL_TABLE_NAME} (
          user_id INT64 NOT NULL,
          order_date DATE NOT NULL,
          total_orders INT64,
          total_spent NUMERIC
        ) PRIMARY KEY (user_id, order_date) ;;
      sql_step:
        -- Secondary index for fast date-range filtering
        CREATE INDEX idx_pdt_user_orders_date ON ${SQL_TABLE_NAME} (order_date) ;;
      sql_step:
        INSERT INTO ${SQL_TABLE_NAME} (user_id, order_date, total_orders, total_spent)
        SELECT user_id, CAST(created_at AS DATE), COUNT(*), SUM(amount)
        FROM orders
        GROUP BY 1, 2 ;;
    }
  }
}
```

### C. Snowflake (`cluster_keys`)
Snowflake manages micro-partitions automatically, but tables `> 1 TB` with degraded pruning **MUST** declare `cluster_keys`:

```lookml
derived_table: {
  sql: SELECT order_date, user_id, SUM(amount) AS total_amount FROM orders GROUP BY 1, 2 ;;
  datagroup_trigger: daily_etl_datagroup
  cluster_keys: ["order_date", "user_id"]
}
```

---

## 3. Incremental PDTs & The Cold-Start Load Protocol

SQL-based Incremental PDTs require **three mandatory LookML elements** to pass `validate_project`:
1. `increment_key`: Name of a time-based LookML `dimension` or `dimension_group` timeframe defined in the same view (e.g., `"transaction_date"`).
2. `increment_offset`: Lookback periods rebuilt on each incremental run to capture late-arriving records (e.g., `3`).
3. `{% incrementcondition %} <sql_date_column> {% endincrementcondition %}` inside the `WHERE` clause: Evaluates to `TRUE` during the initial full build and injects the incremental lookback predicate on subsequent builds.

### Preventing Initial Build Crashes (2-Phase Cold-Start Cap)
Because `{% incrementcondition %}` evaluates to `TRUE` on the first build, an uncapped initial build over multi-terabyte history can time out. Apply the 2-phase Cold-Start protocol:

```text
[Phase 1: Deploy with 30-Day Static WHERE Cap + incrementcondition] -> [Initial Table Builds in Seconds] -> [Backfill History in Warehouse Batches] -> [Phase 2: Remove Static 30-Day Cap, Keep incrementcondition]
```

```lookml
view: pdt_historical_transactions {
  derived_table: {
    sql:
      SELECT
        transaction_id,
        transaction_date,
        user_id,
        amount
      FROM @{DATASET_NAME}.raw_transactions
      WHERE {% incrementcondition %} transaction_date {% endincrementcondition %}
        -- PHASE 1 COLD-START CAP: Remove this static filter in Phase 2 after warehouse backfill
        AND transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) ;;
    datagroup_trigger: daily_etl_datagroup
    increment_key: "transaction_date"
    increment_offset: 3
    partition_keys: ["transaction_date"]
    cluster_keys: ["user_id"]
  }

  dimension_group: transaction {
    type: time
    datatype: date
    timeframes: [raw, date, month, year]
    sql: ${TABLE}.transaction_date ;;
  }
}
```

### Phase 3: Architectural Offloading (ELT Outsourcing)
When a dataset exceeds warehouse bytes-billed or slot limits even in batched backfills, **do not force Looker's PDT regenerator to build it**. Offload materialization to the warehouse ELT layer (dbt, scheduled queries, or materialized views) and map Looker via a lightweight read-only `sql_table_name` view.
