# LookML Testing Suite (Data Integrity & Quality Assurance)

LookML unit tests (`test:` blocks) run automated queries against your warehouse to verify that your semantic model behaves as expected and that primary keys remain unique across joins before deploying to production.

---

## 1. Quality Standards

- **Location:** Define tests in `tests/<explore_name>.test.lkml` (one suite file per Explore).
- **Model Inclusion:** Include all test suites in `<project_name>.model.lkml` via `include: "/tests/*.test.lkml"`.
- **Scan Cost Guardrail:** Add bracketed date filters (`filters: [orders.created_date: "7 days"]`) inside `explore_source:` on large fact tables unless full-history validation is strictly required.
- **Compiler Grammar Rule:** In Looker's LookML grammar, `assert:` only supports the `expression:` subparameter. Never place `description:` inside `assert:` (document assertions with `#` comments instead).

---

## 2. Core Test Configuration

Every LookML test consists of an `explore_source:` query and one or more `assert:` blocks:

```lookml
test: <test_name> {
  explore_source: <explore_name> {
    column: <column_alias> { field: <view_name>.<field_name> }
    filters: [<view_name>.<date_field>: "7 days"]
  }
  # Explain what this assertion validates
  assert: <assertion_name> {
    expression: ${<view_name>.<field_name>} = 1 ;;
  }
}
```

---

## 3. Mandatory Test Scenarios

### Scenario A: Primary Key Uniqueness (The Anti-Fanout Shield)
Verifies that primary keys remain unique after Explore joins, preventing double-counting fanout errors caused by misconfigured `one_to_many` relationships.

```lookml
test: orders_pk_is_unique {
  explore_source: orders {
    column: order_id { field: orders.order_id }
    column: orders_count { field: orders.orders_count }
    filters: [orders.created_date: "7 days"]
  }
  # Verifies that each primary key appears once without join duplication
  assert: pk_uniqueness_verified {
    expression: ${orders.orders_count} = 1 ;;
  }
}
```

### Scenario B: Composite Primary Key Validation
When a physical table lacks a single-column unique ID, synthesize a hidden composite `primary_key: yes` dimension in `views/refined/<view>_rfn.view.lkml` and validate its uniqueness:

**`views/refined/sessions_rfn.view.lkml`**:
```lookml
include: "/views/raw/sessions.view.lkml"

view: +sessions {
  dimension: session_event_pk {
    primary_key: yes
    hidden: yes
    type: string
    sql: CONCAT(CAST(${session_id} AS STRING), '|', CAST(${event_id} AS STRING)) ;;
  }
}
```

**`tests/sessions.test.lkml`**:
```lookml
test: sessions_pk_is_unique {
  explore_source: sessions {
    column: session_event_pk { field: sessions.session_event_pk }
    column: sessions_count { field: sessions.sessions_count }
    filters: [sessions.created_date: "yesterday"]
  }
  # Ensures the synthesized composite primary key is unique
  assert: composite_pk_uniqueness_verified {
    expression: ${sessions.sessions_count} = 1 ;;
  }
}
```

### Scenario C: Business Logic & Boundary Tests
Verify mathematical invariants (for example, gross margin never exceeds total revenue and counts are non-negative):

```lookml
test: margin_is_mathematically_valid {
  explore_source: orders {
    column: revenue_total { field: orders.revenue_total }
    column: gross_margin_total { field: orders.gross_margin_total }
    filters: [orders.created_date: "yesterday"]
  }
  # Asserts that gross margin never exceeds total revenue
  assert: margin_does_not_exceed_revenue {
    expression: ${orders.gross_margin_total} <= ${orders.revenue_total} ;;
  }
}
```

---

## 4. Quality Assurance Checklist
- [ ] Saved in `tests/<explore_name>.test.lkml` and included via `include: "/tests/*.test.lkml"`.
- [ ] Every Explore has a primary-key uniqueness test (`= 1`) with a bounded date filter on large tables.
- [ ] Every `assert:` block contains only `expression:` (using `#` comments rather than `description:`).
