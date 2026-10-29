# Portable Project Scaffolding Templates

Use these canonical templates when scaffolding a greenfield LookML project directly via Looker MCP (`create_project_file`) or local file tools—no local Python runtime is required. Always substitute `<project_name>`, `<connection_name>`, `<dataset_name>`, and `<table_name>` with verified user or warehouse values.

---

## 1. Project Manifest (`manifest.lkml`)

```lookml
project_name: "<project_name>"

constant: CONNECTION_NAME {
  value: "<connection_name>"
  export: override_optional
}

constant: DATASET_NAME {
  value: "<dataset_name>"
  export: override_optional
}

constant: DRILL_LINE_VIZ {
  value: "{% assign vis_config = '{\"type\":\"looker_line\",\"x_axis_gridlines\":false,\"y_axis_gridlines\":true,\"show_view_names\":false,\"show_y_axis_labels\":true,\"interpolation\":\"linear\"}' %}"
}

constant: DRILL_COLUMN_VIZ {
  value: "{% assign vis_config = '{\"type\":\"looker_column\",\"x_axis_gridlines\":false,\"y_axis_gridlines\":true,\"show_view_names\":false,\"show_value_labels\":true}' %}"
}

constant: DRILL_PIE_VIZ {
  value: "{% assign vis_config = '{\"type\":\"looker_pie\",\"value_labels\":\"legend\",\"label_type\":\"labPer\",\"inner_radius\":50,\"show_view_names\":false}' %}"
}

constant: DRILL_GRID_VIZ {
  value: "{% assign vis_config = '{\"type\":\"looker_grid\",\"show_row_numbers\":true,\"size_to_fit\":true,\"table_theme\":\"white\",\"truncate_text\":false}' %}"
}
```

---

## 2. Clean Model File (`<project_name>.model.lkml`)

```lookml
connection: "@{CONNECTION_NAME}"

include: "/views/refined/*.view.lkml"
include: "/explores/*.explore.lkml"
include: "/tests/*.test.lkml"
include: "/dashboards/*.dashboard.lookml"

datagroup: default_etl_datagroup {
  sql_trigger: SELECT CURRENT_DATE ;; # Replace with lightweight warehouse ETL metadata trigger
  max_cache_age: "24 hours"
  description: "Default ETL-aligned cache policy."
}

persist_with: default_etl_datagroup
```

---

## 3. Raw View (`views/raw/<table_name>.view.lkml`)

Map physical database columns 1:1 with `primary_key: yes` first and zero measures or presentation logic:

```lookml
view: orders {
  sql_table_name: @{DATASET_NAME}.orders ;;

  dimension: order_id {
    primary_key: yes
    type: string
    sql: ${TABLE}.order_id ;;
  }

  dimension: user_id {
    type: string
    sql: ${TABLE}.user_id ;;
  }

  dimension: sale_amount {
    type: number
    sql: ${TABLE}.sale_amount ;;
  }

  dimension_group: created {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.created_at ;;
  }
}
```

---

## 4. Refined View (`views/refined/<table_name>_rfn.view.lkml`)

Follow strict top-to-bottom sequencing (`1. Keys -> 2. Dimensions -> 3. Measures -> 4. Filters & Parameters -> 5. Sets`) and wire PoP logic from `pop_engine.md`:

```lookml
include: "/views/raw/orders.view.lkml"

view: +orders {
  # 1. KEYS
  dimension: order_id {
    hidden: yes
    description: "Unique primary key for each order."
  }

  dimension: user_id {
    hidden: yes
    description: "Foreign key referencing users.user_id."
  }

  # 2. DIMENSIONS
  dimension: sale_amount {
    label: "Order Sale Amount"
    description: "Gross transaction amount for the order."
    value_format_name: usd
  }

  # Add hidden PoP boundary dimensions & pop_period_group here (see pop_engine.md)

  # 3. MEASURES
  measure: orders_count {
    label: "Orders Count"
    description: "Total count of orders."
    type: count
    value_format_name: decimal_0
    drill_fields: []
    link: {
      label: "Orders Trend Over Time"
      url: "@{DRILL_LINE_VIZ}{{ link }}&fields=orders.created_date,orders.orders_count&sorts=orders.created_date+asc&limit=500&vis_config={{ vis_config | encode_uri }}&toggle=dat,pik,vis"
    }
    link: {
      label: "View Order Details (Table)"
      url: "@{DRILL_GRID_VIZ}{{ link }}&fields=orders.order_id,orders.created_time,orders.sale_amount&sorts=orders.created_time+desc&limit=50&vis_config={{ vis_config | encode_uri }}&toggle=dat,pik,vis"
    }
  }

  measure: revenue_total {
    label: "Total Revenue"
    description: "Sum of order sale amounts."
    type: sum
    sql: ${sale_amount} ;;
    value_format_name: usd
    drill_fields: []
    link: {
      label: "Revenue Trend Over Time"
      url: "@{DRILL_LINE_VIZ}{{ link }}&fields=orders.created_date,orders.revenue_total&sorts=orders.created_date+asc&limit=500&vis_config={{ vis_config | encode_uri }}&toggle=dat,pik,vis"
    }
  }

  # Add PoP selected, previous, and pop_change measures here (see pop_engine.md)

  # 4. FILTERS & PARAMETERS
  filter: pop_date_filter {
    view_label: "_PoP"
    label: "Comparison Date Filter"
    description: "Current date window for Period-over-Period comparison."
    type: date
    default_value: "7 days"
  }

  parameter: pop_compare_to {
    view_label: "_PoP"
    label: "Compare To"
    description: "Offset interval for previous period comparison."
    type: string
    allowed_value: { value: "Yesterday" }
    allowed_value: { value: "Week" }
    allowed_value: { value: "Month" }
    allowed_value: { value: "Year" }
    default_value: "Year"
  }

  # 5. SETS
  set: detail {
    fields: [order_id, created_time, sale_amount]
  }
}
```

---

## 5. Modular Explore (`explores/<explore_name>.explore.lkml`) & Project `README.md`

```lookml
include: "/views/refined/*.view.lkml"

explore: orders {
  label: "Orders & Revenue"
  description: "Order transactions joined to customer attributes."

  join: users {
    type: left_outer
    relationship: many_to_one
    sql_on: ${orders.user_id} = ${users.user_id} ;;
  }
}
```

For the target LookML repository's root `README.md`, document: (1) supported SQL dialect and required warehouse tables, (2) overriding `CONNECTION_NAME` and `DATASET_NAME` in `manifest.lkml`, (3) datagroup/PDT refresh schedules, (4) Explore and KPI definitions, and (5) validation commands (`looker-cli project validate <project_name>`).
