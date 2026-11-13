# LookML Field Sets (`set:`)

Sets are reusable lists of fields (dimensions, measures, and filters) defined within a view and referenced across `drill_fields` and Explore `fields:` scoping.

## 1. Syntax & Composition Rules

```lookml
set: set_name {
  fields: [field_1, field_2, other_set*, -excluded_field]
}
```

- **Include All (`set_name*`):** Expands all fields contained in `set_name`.
- **Exclude (`-field_name`):** Removes a specific field or subset (`-other_set*`) from the list.
- **Cross-View Reference (`view_name.set_name*`):** References a set from another view (best used at the Explore level where both views are guaranteed to be joined).

---

## 2. Core Use Cases & Best Practices

### 1. Standardized Drill Paths (`drill_fields: [detail*]`)
Every view should define a default drill set (commonly named `detail` or `[view_name]_details`) containing the primary key and 4–6 key descriptive attributes, referenced by measures in that view:

```lookml
view: orders {
  set: detail {
    fields: [order_id, created_date, status, sale_price]
  }

  measure: count_orders {
    type: count
    drill_fields: [detail*]
    description: "Total count of orders."
  }
}
```

### 2. Curating Explore Field Visibility (`fields:`)
Use sets at the `explore:` or `join:` level to control which fields appear in the UI field picker or to exclude sensitive columns without hiding them globally across all Explores:

```lookml
explore: customer_support_orders {
  view_name: orders
  description: "Orders curated for customer support agents."

  # Exclude sensitive financial columns from this specific Explore
  fields: [ALL_FIELDS*, -orders.cost, -orders.gross_margin, -users.ssn]

  join: users {
    type: left_outer
    relationship: many_to_one
    sql_on: ${orders.user_id} = ${users.user_id} ;;
    # Expose only the curated support set from the joined users view
    fields: [users.support_profile*]
  }
}
```

### 3. Cumulative Sets & Avoiding Fragile Cross-View Dependencies
- **Keep View Sets Self-Contained:** Define sets inside a view using only that view's own fields (`[id, name, email]`) so the view never breaks if used in an Explore where a foreign view is not joined.
- **Combine Sets in the Explore or Refined Layer:** Build composite drill sets (`fields: [detail*, users.user_summary*]`) in the refinement layer or Explore file.
