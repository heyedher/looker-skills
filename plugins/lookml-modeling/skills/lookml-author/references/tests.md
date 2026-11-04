# LookML Data Tests (`test:`)

LookML data tests (`test:`) verify semantic model integrity, primary key uniqueness across joins, and business calculation accuracy before changes are deployed to production.

## 1. File Organization & Inclusion

- **File Naming:** Place test suites in `tests/[explore_name].test.lkml` (one test file per Explore, e.g., `tests/orders.test.lkml`).
- **Model Inclusion:** Include the test files in your `.model.lkml` (`include: "/tests/*.test.lkml"`) or inside the corresponding `.explore.lkml` file so `run_lookml_tests` discovers them.
- **Execution:** Run tests via Looker MCP (`get_lookml_tests`, `run_lookml_tests`) or CLI (`looker-cli api project run_lookml_test {project_id}`).

---

## 2. Anatomy of a LookML Data Test

Every `test:` block contains an `explore_source:` query and one or more `assert:` blocks whose `expression:` must evaluate to `yes` (`true`) for **every row** returned by the query:

```lookml
test: test_name {
  explore_source: explore_name {
    column: local_alias { field: view_name.field_name }
    filters: [view_name.filter_field: "filter_expression"]
  }
  assert: assertion_name {
    expression: ${view_name.field_name} > 0 ;;
  }
}
```

> **Performance Guardrail:** Always include a Partition/Date filter (e.g., `orders.created_date: "7 days"`) in `explore_source` when testing large warehouse tables to prevent full-table scans during CI validation.

---

## 3. Three Core Categories of LookML Tests

### A. Primary Key Uniqueness & Fanout Prevention (Critical)
Group by the base view's primary key and assert that `count` equals `1`. This catches unintended `one_to_many` join fanouts:

```lookml
test: orders_pk_is_unique {
  explore_source: orders {
    column: order_id { field: orders.order_id }
    column: count_orders { field: orders.count_orders }
    filters: [orders.created_date: "7 days"]
    sorts: [orders.count_orders: desc]
    limit: 1
  }

  assert: order_id_Has_no_duplicates {
    expression: ${orders.count_orders} = 1 ;;
  }
}
```

### B. Metric Accuracy & Non-Negative Bounds
Verify that key aggregates satisfy expected bounds over a known time window:

```lookml
test: completed_revenue_is_positive {
  explore_source: orders {
    column: total_completed_revenue { field: orders.total_completed_revenue }
    filters: [orders.created_date: "yesterday"]
  }

  assert: revenue_greater_than_zero {
    expression: ${orders.total_completed_revenue} > 0 ;;
  }
}
```

### C. Business Logic Invariants
Verify relationships between measures (for example, net revenue or gross margin never exceeding gross revenue):

```lookml
test: margin_does_not_exceed_revenue {
  explore_source: orders {
    column: created_date { field: orders.created_date }
    column: total_revenue { field: orders.total_revenue }
    column: total_margin { field: orders.total_margin }
    filters: [orders.created_date: "30 days"]
  }

  assert: valid_margin_bound {
    expression: ${orders.total_margin} <= ${orders.total_revenue} ;;
  }
}
```
