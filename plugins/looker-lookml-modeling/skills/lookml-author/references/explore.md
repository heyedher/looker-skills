# LookML Explores, Joins, Aggregate Tables & Row-Level Security

This reference covers defining LookML Explores (`explore:`), configuring joins, building aggregate awareness tables (`aggregate_table:`), unnesting arrays, and applying row-level security (`access_filter`).

## 1. Core Explore & Join Standards

1. **Naming & Required Metadata:**
   - Use `snake_case` for the Explore name.
   - **`description:` (100% Coverage):** Every Explore must have a clear description.
   - **`label:`**: User-friendly UI name.
   - **`view_name:`**: Explicitly specify the base view (defaults to the Explore name).
2. **Joins (`join: view_name`):**
   - **`relationship:` (Required):** Explicitly set `many_to_one`, `one_to_one`, `one_to_many`, or `many_to_many` so Looker computes symmetric aggregates accurately and prevents fanout inflation.
   - **`sql_on:` (Required for standard joins):** Always use LookML field substitution syntax (`${left_view.key} = ${right_view.key} ;;`).
   - **`type:`**: Defaults to `left_outer` (preferred to preserve base table rows). Use `inner`, `full_outer`, or `cross` only when intentionally required.
   - **`from:` vs. `view_label:`**: Do **not** use `from:` merely to change how a view name appears in the UI—use `view_label:` instead. Reserve `from:` for role-playing/self-joins (e.g., joining `users` twice as `buyers` and `sellers`), polymorphic joins, or rescoping extensions.
   - **`fields:`**: Restrict exposed fields from a joined view when needed (`fields: [users.detail*]` or `fields: [ALL_FIELDS*, -users.ssn]`).

---

## 2. Filtering, Security & Advanced Join Patterns

- **`always_filter:`**: Requires users to supply a filter value with a default (users can change the value, but cannot remove the filter).
- **`sql_always_where:` / `sql_always_having:`**: Enforces an immutable `WHERE` or `HAVING` restriction that end users cannot see or bypass.
- **`access_filter:` (Row-Level Security):** Binds a LookML dimension to a Looker Admin `user_attribute` to filter rows dynamically per user.
- **`UNNEST` / `LATERAL FLATTEN`:** Use a bare `sql:` parameter inside a `join:` (with `relationship: one_to_many`) to flatten repeated/array columns in BigQuery or Snowflake.
- **Extending Explores (`extends: [base_explore]`):** Share common joins across specialized Explores without duplicating join blocks.

---

## 3. Aggregate Awareness (`aggregate_table:`)

Aggregate tables pre-aggregate high-traffic combinations of dimensions and measures so Looker automatically routes matching dashboard/Explore queries to smaller summary tables.

- **`query:`**: Defines the rollup `dimensions:`, `measures:` (use base `sum`/`count` measures), and optional `filters:`. Include the finest needed time grain (e.g., `created_date`, which Looker can automatically roll up to `week`, `month`, or `year`) and any commonly filtered dimensions.
- **`materialization:`**: Configure `datagroup_trigger:`, dialect `partition_keys:` / `cluster_keys:`, and optional incremental settings (`increment_key:`, `increment_offset:`).

---

## 4. Examples

### Standard Explore with Role-Playing Joins (`from:`), Filters & RLS

```lookml
explore: orders {
  label: "Orders & Fulfillment"
  description: "Order transactions joined with buyer, seller, and line-item details."
  view_name: orders
  persist_with: ecommerce_etl

  # Editable default filter in the UI
  always_filter: {
    filters: [orders.created_date: "30 days"]
  }

  # Immutable WHERE restriction
  sql_always_where: ${orders.is_test_order} = false ;;

  # Row-Level Security via user_attribute
  access_filter: {
    field: orders.sales_region
    user_attribute: allowed_sales_regions
  }

  # Role-playing join: Users as Buyers
  join: buyers {
    from: users
    type: left_outer
    relationship: many_to_one
    sql_on: ${orders.buyer_id} = ${buyers.user_id} ;;
    view_label: "Buyer"
  }

  # Role-playing join: Users as Sellers
  join: sellers {
    from: users
    type: left_outer
    relationship: many_to_one
    sql_on: ${orders.seller_id} = ${sellers.user_id} ;;
    view_label: "Seller"
  }
}
```

### Array Unnesting (BigQuery `UNNEST` & Snowflake `LATERAL FLATTEN`)

```lookml
explore: orders_with_nested_items {
  view_name: orders
  description: "Unnests repeated line items embedded inside the orders table."

  # BigQuery Standard SQL UNNEST
  join: items {
    sql: LEFT JOIN UNNEST(${orders.items}) AS items ;;
    relationship: one_to_many
  }

  # Snowflake LATERAL FLATTEN equivalent:
  # join: items {
  #   sql: , LATERAL FLATTEN(input => ${orders.items}) AS items ;;
  #   relationship: one_to_many
  # }
}
```

### Aggregate Table with Incremental Partitioning

```lookml
explore: orders {
  description: "Orders Explore with monthly aggregate awareness."
  aggregate_table: monthly_sales_rollup {
    query: {
      dimensions: [orders.created_date, orders.status, products.category]
      measures: [orders.total_revenue, orders.count]
      filters: [orders.created_date: "2 years"]
    }
    materialization: {
      datagroup_trigger: ecommerce_etl
      partition_keys: ["created_date"]
      increment_key: "created_date"
      increment_offset: 3
    }
  }
}
```
