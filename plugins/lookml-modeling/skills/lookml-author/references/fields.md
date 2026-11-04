# LookML Fields, Timeframes, Durations & Value Formatting

This reference covers LookML field types (`dimension`, `measure`, `dimension_group`, `filter`, `parameter`) and display formatting (`value_format_name`, `value_format`, `named_value_format`, and Liquid `html`).

## 1. Field Types & Role of the `sql` Parameter

| Field Type | SQL Generation Phase | `sql` References Allowed | Can Reference Measures? |
| :--- | :--- | :--- | :--- |
| **`dimension`** | `SELECT` & `GROUP BY` | `${TABLE}.col`, `${other_dimension}` | **No** |
| **`dimension_group`** | `SELECT` & `GROUP BY` | Timestamp/date columns (`time`) or `sql_start` / `sql_end` (`duration`) | **No** |
| **`measure` (Aggregated)** | `SELECT` (`SUM`, `AVG`, `COUNT(DISTINCT)`) | `${dimension_name}` (preferred) or `${TABLE}.col` (`sql` ignored on `type: count`) | **No** |
| **`measure` (`type: number`)** | `SELECT` (Post-aggregation expression) | **Other Measures** (e.g., `${total_revenue} / NULLIF(${count}, 0)`) | **Yes** |
| **`filter`** | `WHERE` / `HAVING` via `{% condition %}` | Rarely used directly; drives templated filters | **No** |
| **`parameter`** | None directly (injected via Liquid) | None (`allowed_value` choices injected via `{% parameter %}`) | **No** |

---

## 2. Dimensions & Measures Standards

### Dimensions (`dimension:`)
- **Naming:** `snake_case`. Prefix booleans with `is_` or `has_` (`is_active`, `has_churned`).
- **Required Parameters:** 100% coverage of `sql:`, `type:` (`string`, `number`, `yesno`, `tier`, `location`, `distance`), and `description:`.
- **Primary Keys & Visibility:** Place primary key first (`primary_key: yes`, `group_label: "IDs"`). Hide raw technical IDs or intermediate helper fields with `hidden: yes`.

### Measures (`measure:`)
- **Naming:** Prefix counts with `count_`, sums with `total_`, and averages with `avg_`.
- **Required Parameters:** `type:` (`count`, `count_distinct`, `sum`, `average`, `min`, `max`, `number`), `description:`, and `drill_fields: [set_name*]` on primary count/sum metrics.
- **Filtered Measures:** Use native `filters: [status: "complete"]` inside the measure definition rather than `CASE WHEN` inside `sql:` so Looker can still apply symmetric aggregates.

---

## 3. Dimension Groups (`type: time` & `type: duration`)

### A. Time Dimension Groups (`type: time`)
- **Explicit Timeframes:** Always declare `timeframes: [raw, time, date, week, month, quarter, year]`. Never omit `raw` (Looker's default omits `raw`, breaking timestamp comparisons and duration calculations).
- **Naming:** Strip `_at`, `_date`, or `_timestamp` from the group name (`dimension_group: created`, **not** `created_at`, so Looker generates `created_date` instead of `created_at_date`).
- **Datatype & Date Strings:** Set `datatype: date` (timeframes restricted to `[date, week, month, quarter, year]`) when the column has no time component. If stored as a string, cast in `sql:` (`CAST(${TABLE}.date_str AS DATE)`).

### B. Duration Dimension Groups (`type: duration`) — Mandatory for Date Diffs
- **Critical Rule:** Whenever calculating time elapsed or date differences (`days_since_signup`, `months_between_orders`, `processing_time`), you **must** use `dimension_group` with `type: duration` (`intervals`, `sql_start`, `sql_end`). **Never** write manual `DATEDIFF` or `DATE_DIFF` SQL inside a standard `dimension`.
- **Generated Fields & Naming:** Looker prepends the pluralized interval to the group name (`dimension_group: since_signup` with `intervals: [day, month, year]` generates `${days_since_signup}`, `${months_since_signup}`, and `${years_since_signup}`). Never put the word `duration` in the group name.

---

## 4. Filters, Parameters & Value Formatting

- **Templated Filters (`filter:`):** Pair `filter: date_filter { type: date }` with `WHERE {% condition date_filter %} created_at {% endcondition %}` inside derived tables.
- **Parameters (`parameter:`):** Define `type: unquoted` (or `string`/`number`) with `allowed_value:` options and reference `{% parameter param_name %}` or `param_name._parameter_value` in Liquid.
- **Value Formats:**
  - Prefer built-in **`value_format_name:`** (`usd`, `usd_0`, `eur`, `gbp`, `decimal_0`, `decimal_2`, `percent_1`, `percent_2`, `id`).
  - Use **`value_format:`** for custom Excel format strings (`"$#,##0.00;($#,##0.00)"`, `"0.00,,\" M\""` for millions, `"0.00,\" K\""` for thousands).
  - Use model-level **`named_value_format:`** with `strict_value_format: yes` when a format (such as zero-padded codes) must ignore user locale swapping.

---

## 5. Comprehensive Example

```lookml
view: orders {
  sql_table_name: `project.dataset.orders` ;;

  dimension: order_id {
    primary_key: yes
    type: number
    sql: ${TABLE}.id ;;
    group_label: "IDs"
    description: "Unique identifier for the order."
  }

  dimension_group: created {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.created_at ;;
    description: "Timestamp when the order was placed."
  }

  dimension_group: fulfillment_lead_time {
    type: duration
    intervals: [hour, day, week]
    sql_start: ${created_raw} ;;
    sql_end: ${shipped_raw} ;;
    description: "Elapsed time between order creation and shipment."
  }

  dimension: sale_price {
    type: number
    sql: ${TABLE}.sale_price ;;
    value_format_name: usd
    description: "Item sale price in USD."
  }

  dimension: status {
    type: string
    sql: ${TABLE}.status ;;
    description: "Order lifecycle status (pending, complete, cancelled)."
  }

  measure: count_orders {
    type: count
    drill_fields: [order_id, created_date, status, sale_price]
    description: "Total count of orders."
  }

  measure: total_revenue {
    type: sum
    sql: ${sale_price} ;;
    value_format_name: usd
    drill_fields: [order_id, created_date, status, sale_price]
    description: "Total gross revenue across all orders."
  }

  measure: total_completed_revenue {
    type: sum
    sql: ${sale_price} ;;
    filters: [status: "complete"]
    value_format_name: usd
    description: "Total revenue from completed orders only."
  }

  measure: avg_order_value {
    type: number
    sql: ${total_revenue} / NULLIF(${count_orders}, 0) ;;
    value_format_name: usd
    description: "Average revenue per order."
  }
}
```
