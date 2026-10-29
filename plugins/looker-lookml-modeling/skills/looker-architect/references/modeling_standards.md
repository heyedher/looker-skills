# Enterprise LookML Modeling Standards (The 11 Golden Rules)

This reference provides the exact directory layout and LookML implementation patterns for the 11 Architectural Golden Rules enforced by `looker-architect`.

---

## Standard Modular Project Layout

```text
<project_name>/
|-- views/
|   |-- raw/                         # 1:1 physical table column mappings only
|   |   `-- <table_name>.view.lkml
|   `-- refined/                     # Business logic via view: +<table_name>
|       `-- <table_name>_rfn.view.lkml
|-- explores/                        # One modular explore per file
|   `-- <explore_name>.explore.lkml
|-- tests/                           # One LookML data test suite per explore
|   `-- <explore_name>.test.lkml
|-- dashboards/                      # Version-controlled native tabbed dashboards
|   `-- <dashboard_name>.dashboard.lookml
|-- <project_name>.model.lkml        # Connection constant, datagroups, includes only
|-- manifest.lkml                    # Connection/dataset & visual drill constants
`-- README.md                        # End-user setup, constants, and KPI catalog
```

---

## Rule 1: Centralized Connection & Dataset Constants

Never hardcode connection or schema/dataset names inside `.model.lkml` or view files. Declare them in `manifest.lkml` with `export: override_optional`.

```lookml
# manifest.lkml
project_name: "my_lookml_project"

constant: CONNECTION_NAME {
  value: "my_connection"
  export: override_optional
}

constant: DATASET_NAME {
  value: "my_dataset"
  export: override_optional
}
```

```lookml
# my_lookml_project.model.lkml
connection: "@{CONNECTION_NAME}"

# views/raw/users.view.lkml
view: users {
  sql_table_name: @{DATASET_NAME}.users ;;
}
```

---

## Rule 2: Visual Drill Constants & `drill_fields: []` Quirk

Define reusable JSON visualization configurations in `manifest.lkml` and attach 2-3 custom `link` blocks to core measures. Always declare `drill_fields: []` so the Looker UI activates custom hyperlinks (see `visual_drilling.md`).

```lookml
# manifest.lkml
constant: DRILL_COLUMN_VIZ {
  value: "{% assign vis_config = '{\"type\":\"looker_column\",\"x_axis_gridlines\":false,\"y_axis_gridlines\":true,\"show_view_names\":false,\"show_value_labels\":true}' %}"
}

# views/refined/users_rfn.view.lkml
view: +users {
  measure: users_count {
    type: count
    value_format_name: decimal_0
    drill_fields: []
    link: {
      label: "Users by Country (Column Chart)"
      url: "@{DRILL_COLUMN_VIZ}{{ link }}&fields=users.country,users.users_count&sorts=users.users_count+desc&limit=10&vis_config={{ vis_config | encode_uri }}&toggle=dat,pik,vis"
    }
  }
}
```

---

## Rule 3 & Rule 4: Raw vs. Refined Separation & Field Sequencing

- **Raw Views (`views/raw/`):** 1:1 physical column dimensions only, with `primary_key: yes` first. Zero measures, labels, or custom SQL calculations.
- **Refined Views (`views/refined/`):** Use `view: +<view_name>` organized strictly top-to-bottom:
  1. **Keys** (`primary_key: yes`, composite PKs, hidden foreign keys)
  2. **Dimensions** (business attributes, `group_label`, custom buckets)
  3. **Measures** (native aggregations, ratios, PoP measures, visual drills)
  4. **Filters & Parameters** (`pop_date_filter`, `pop_compare_to`, dynamic inputs)
  5. **Sets** (`set: detail { ... }`)

Within each section, sort fields alphabetically (`A-Z`) or group consistently by `group_label`.

---

## Rule 5: Substitution Operator Inheritance (`${field_name}`)

Always reference LookML fields via `${field_name}` rather than raw `${TABLE}.column_name` so types, descriptions, and dependencies propagate automatically.

```lookml
# CORRECT: Inherits base field metadata and tracks LookML lineage
dimension: sale_price {
  type: number
  sql: ${TABLE}.sale_price ;;
  description: "Unit sale price."
  value_format_name: usd
}

measure: revenue_total {
  type: sum
  sql: ${sale_price} ;;
  value_format_name: usd
}

# INCORRECT: Bypasses LookML semantic layer (sql: ${TABLE}.sale_price ;;)
```

---

## Rule 6 & Rule 7: Native Aggregations & Naming Conventions

- Use `snake_case` for all file names and LookML identifiers, with explicit measure suffixes (`_count`, `_total`, `_amount`).
- Use native Looker aggregation types (`type: sum`, `type: average`, `type: count`, `type: count_distinct`) rather than embedding `SUM(...)` or `AVG(...)` inside `type: number`. Writing SQL aggregates inside `type: number` disables Looker Symmetric Aggregations on one-to-many joins and causes fan-outs.

```lookml
# CORRECT
measure: benchmark_average {
  type: average
  sql: ${benchmark_score} ;;
  value_format_name: decimal_2
}

# INCORRECT: Disables Symmetric Aggregations
# measure: benchmark_average { type: number sql: AVG(${TABLE}.benchmark_score) ;; }
```

---

## Rule 8: Safe Division, Aggregate Ratios & Mandatory Value Formatting

1. **Safe Division:** Guard every denominator with `SAFE_DIVIDE(num, den)` (BigQuery) or `1.0 * num / NULLIF(den, 0)` (ANSI/Snowflake/Redshift/PostgreSQL).
2. **Aggregate Ratios Only:** Compute ratios in `type: number` over already-aggregated measures—never `type: average` over a row-level ratio column.
3. **100% Value Formatting:** Every numeric measure must declare `value_format_name` or `value_format`:
   - Ratios/Percentages: `value_format_name: percent_1` or `percent_2`
   - Decimals/Averages: `value_format_name: decimal_2` or `decimal_1`
   - Counts/Integers: `value_format_name: decimal_0`
   - Currencies: `value_format_name: usd` or `usd_0`
   - Custom Units: `value_format: "#,##0.00 \"s\""`, `"#,##0.0 \"ms\""`, `"#,##0.00 \"GB\""`, or `"[>=1000000]#,##0.0,,\"M\";[>=1000]#,##0.0,\"K\";#,##0"`

```lookml
measure: conversion_rate {
  type: number
  sql: 1.0 * ${orders_count} / NULLIF(${sessions_count}, 0) ;;
  value_format_name: percent_1
  description: "Completed orders divided by total sessions."
}
```

---

## Rule 9, Rule 10 & Rule 11: Explore Governance, Tabbed PoP Dashboards & Real SQL

- **Rule 9 (Modular Explores & Join Pruning):** Model each physical table in its own view and join them inside `explores/<name>.explore.lkml` with explicit `relationship:` (`many_to_one`, `one_to_one`, `one_to_many`) and `sql_on:` using `${view.field}`. Never define `explore:` blocks directly inside `.model.lkml`.
- **Rule 10 (Tabbed Dashboards & PoP Scorecards):** Use `layout: newspaper` and native `tabs:` (resetting coordinates at `row: 0, col: 0` on every tab; never HTML navigation banners). Every KPI `single_value` tile must query `[current_measure, pop_change_measure]` with `show_comparison: true`, `comparison_type: change`, and dashboard date filter mapped to `pop_date_filter` (`dashboard_standards.md`).
- **Rule 11 (No Dummy Constants):** Never hardcode mock constants (`sql: 0.05 ;;` or `sql: 1 ;;`) inside measures or PoP deltas; always implement dynamic SQL backed by real warehouse columns (`pop_engine.md`).
