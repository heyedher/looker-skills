# Liquid Variables & Dynamic LookML (`lookml-liquid`)

Liquid templating enables dynamic SQL generation, conditional HTML formatting, dynamic links, and query-aware optimizations in LookML.

## 1. Syntax & Security Guardrails

- **Output Syntax (`{{ ... }}`):** Inserts a rendered string or value (e.g., `{{ value }}`, `{{ rendered_value }}`).
- **Tag Syntax (`{% ... %}`):** Executes conditional logic, loops, or Looker tags (`{% if %}`, `{% parameter %}`, `{% condition %}`).
- **SQL Injection Guardrail (`| sql_quote`):** Always append `| sql_quote` when injecting user-supplied strings (such as `_filters['view.field']`) into raw SQL literals.
- **Dialect Booleans (`| sql_boolean`):** In dialects requiring literal `TRUE`/`FALSE` (such as BigQuery), append `| sql_boolean` to `_in_query` or `_is_selected` checks (`{{ view.field._in_query | sql_boolean }}`).
- **Avoid Fanout in `link:` Parameters:** Referencing `{{ view.other_field._value }}` inside `link:` forces Looker to add `other_field` to the query's `GROUP BY` clause. Use `{{ row['view.other_field'] }}` when you only need a column already present in the browser table row.

---

## 2. `_in_query` vs. `_is_selected` (Totals Trap)

| Variable | Returns `true` When... | Behavior in Totals Row (Critical Difference) |
| :--- | :--- | :--- |
| **`view.field._in_query`** | Field appears in `SELECT`, `WHERE` filters, or `required_fields`. | **Remains `true`** during Totals calculation if the field contributed to the query. |
| **`view.field._is_selected`** | Field appears in `SELECT` or `required_fields`. | **Returns `false`** in Row/Column/Grand Totals for dimensions because dimensions are stripped from `GROUP BY` when computing totals. |

> **Rule:** Use `_in_query` for table routing or join pruning that must stay consistent between detail rows and Totals.

---

## 3. Liquid Variable Quick Reference

*Usage Contexts: **A** = `action`, **DV** = dashboard `default_value`, **DE** = `description`, **F** = dashboard `filters`, **H** = `html`, **LA** = labels (`label`, `view_label`, `group_label`), **LI** = `link`, **S** = SQL (`sql`, `sql_on`, `sql_table_name`).*

| Variable | Description | Allowed Contexts |
| :--- | :--- | :--- |
| `value` | Raw underlying database value of the field | A, H, LI |
| `rendered_value` | Formatted value (preserves `value_format_name` / `%` / `$`) | A, H, LI |
| `filterable_value` | Value escaped for Looker URL filter strings | A, H, LI |
| `link` / `linked_value` | Default drill link URL / formatted value wrapped in drill link | A, H, LI (and S for `link`) |
| `_filters['view.field']` | User filter expression applied to `view.field` | A, DE, H, LA, LI |
| `{% condition filter_name %} sql_col {% endcondition %}` | Compiles user filter input into a valid SQL boolean expression | S |
| `{% date_start date_filter %}` / `{% date_end date_filter %}` | Extracts start or end boundary timestamp of a date filter | S |
| `{% parameter param_name %}` / `param_name._parameter_value` | Injects selected parameter value / evaluates parameter in `{% if %}` | DE, H, LA, LI, S |
| `_user_attributes['attr_name']` | Current user's attribute value | A, DE, H, LA, LI, S, DV, F |
| `_model._name` / `_view._name` / `_explore._name` / `_field._name` | Current metadata object name | A, DE, H, LA, LI, S |
| `view._in_query` / `view.field._in_query` | `true` if any field in view / specific field is in query or filters | DE, LA, LI, S |
| `view.field._is_selected` / `view.field._is_filtered` | `true` if field is in `SELECT` / `true` if field is in `WHERE` | DE, LA, LI, S |

---

## 4. Common Patterns & Examples

### 1. Dynamic Table Routing (`sql_table_name` with `_in_query`)

```lookml
view: orders {
  sql_table_name:
    {% if orders.created_date._in_query or orders.created_time._in_query %}
      `project.dataset.orders_daily_partitioned`
    {% elsif orders.created_month._in_query %}
      `project.dataset.orders_monthly_rollup`
    {% else %}
      `project.dataset.orders_raw`
    {% endif %} ;;
}
```

### 2. Dynamic Measure & Dimension Selection via `parameter`

```lookml
parameter: metric_selector {
  type: unquoted
  allowed_value: { label: "Total Revenue" value: "revenue" }
  allowed_value: { label: "Order Count" value: "orders" }
  default_value: "revenue"
}

measure: selected_metric {
  label_from_parameter: metric_selector
  type: number
  sql:
    {% if metric_selector._parameter_value == 'revenue' %}
      ${total_revenue}
    {% else %}
      ${count_orders}
    {% endif %} ;;
  description: "Dynamically switches between Total Revenue and Order Count."
}
```

### 3. Conditional HTML Formatting (Preserving `rendered_value`)

```lookml
measure: yoy_growth_rate {
  type: number
  sql: (${current_revenue} - ${prior_revenue}) / NULLIF(${prior_revenue}, 0) ;;
  value_format_name: percent_1
  description: "Year-over-year revenue growth percentage."
  html:
    {% if value < 0 %}
      <span style="color: #b71c1c; font-weight: bold;">▼ {{ rendered_value }}</span>
    {% elsif value > 0 %}
      <span style="color: #1b5e20; font-weight: bold;">▲ {{ rendered_value }}</span>
    {% else %}
      <span>{{ rendered_value }}</span>
    {% endif %} ;;
}
```
