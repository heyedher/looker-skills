# LookML Performance & Aggregate Awareness

When scaffolding greenfield Explores over large fact tables, configure Looker **Aggregate Tables** or Liquid **`_in_query` Dynamic Table Routing** to avoid scanning raw event rows on summary tiles. *(For reactive `EXPLAIN` plan profiling, Symmetric Aggregation audits, and PDT tuning on slow existing queries, use `lookml-performance-optimizer`.)*

---

## 1. Native Aggregate Tables (Aggregate Awareness)

Aggregate Tables let Looker automatically route summary queries to smaller pre-aggregated rollups instead of raw granular tables:

```lookml
explore: orders {
  aggregate_table: rollup_monthly_sales {
    query: {
      dimensions: [created_month, status, products.category]
      measures: [revenue_total, orders_count]
      filters: [orders.created_date: "2 years"]
    }
    materialization: {
      datagroup_trigger: default_etl_datagroup
      partition_keys: ["created_month"]
      increment_key: "created_month"
      increment_offset: 1
    }
  }
}
```

### Key Aggregate Awareness Rules
1. **Timeframe Grain:** Include the finest required grain (e.g., `created_date`); Looker rolls `date` up to `month` or `year` automatically.
2. **Strict Subset Matching:** Looker uses an aggregate table only when every queried and filtered dimension/measure is a subset of the rollup's `query:` block.
3. **Filter Coverage:** Always include common dashboard filter dimensions (`status`, `country`) in `dimensions:`.

---

## 2. Liquid-Based Dynamic Table Routing (`_in_query`)

When routing `sql_table_name` across pre-built warehouse summary tables, evaluate Liquid `_in_query` variables directly in control tags:

```lookml
view: orders {
  sql_table_name:
    {% if orders.created_date._in_query or orders.created_hour._in_query %}
      @{DATASET_NAME}.orders_all_transactions
    {% elsif orders.created_month._in_query %}
      @{DATASET_NAME}.orders_monthly_summary
    {% else %}
      @{DATASET_NAME}.orders_daily_summary
    {% endif %} ;;
}
```

### Critical Rules for Liquid Routing
1. **Never Use `_is_selected` for Table Routing (Totals Bug):** During Grand Totals and Column Totals queries, Looker strips dimensions from `SELECT`, turning `_is_selected` to `false` and routing Totals to the wrong summary table. Always use `_in_query`, which stays `true` whenever a field participates in `SELECT`, `WHERE`, `HAVING`, or `required_fields`.
2. **Liquid Control Tags vs. SQL Output Literals:** Inside `{% if ... %}`, `_in_query` is already a Liquid boolean (`{% if orders.created_date._in_query %}`). Use the `| sql_boolean` filter only inside `{{ ... }}` output tags when emitting a literal SQL `TRUE`/`FALSE` value into a `SELECT` or `WHERE` expression (`{{ orders.created_date._in_query | sql_boolean }}`).
