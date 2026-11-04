# LookML Access Grants (`access_grant:` & `required_access_grants:`)

Access Grants enforce object-level security across Explores, joins, views, and individual fields based on Looker `user_attribute` values. *(For row-level `WHERE` filtering by user attribute, use `access_filter` in [explore.md](explore.md).)*

## 1. Defining & Applying Access Grants

1. **Define at the Model Level (`*.model.lkml`):**
   An `access_grant:` block maps a Looker Admin `user_attribute` to an explicit list of `allowed_values`:
   ```lookml
   access_grant: can_view_financial_pii {
     user_attribute: department
     allowed_values: ["finance", "executive"]
   }
   ```
2. **Enforce on Target Objects (`required_access_grants:`):**
   Attach `required_access_grants: [grant_name]` to any `explore:`, `join:`, `view:`, `dimension:`, `dimension_group:`, `measure:`, or `filter:`.

---

## 2. Security Rules & Behavior

- **Exact Value Matching:** `allowed_values` requires an exact match against the user's attribute value (no wildcards or regex inside `allowed_values`).
- **AND Logic Across Multiple Grants:** When multiple grants are listed (`required_access_grants: [grant_a, grant_b]`), the user must satisfy **every** listed grant to access the object.
- **Hierarchical Inheritance (Additive):** If a `view:` requires `grant_a` and a `dimension:` inside that view requires `grant_b`, a user must hold **both** `grant_a` and `grant_b` to see or query that dimension.
- **Query Failure vs. UI Hiding:** Restricted objects are hidden from the Explore field picker, and saved Looks/dashboards referencing restricted fields fail with a permission error for unauthorized users.

---

## 3. Examples

### View-Level & Join-Level Access Control

```lookml
# In models/enterprise.model.lkml
access_grant: can_view_payroll {
  user_attribute: user_department
  allowed_values: ["hr", "finance", "executive"]
}

# In explores/employees.explore.lkml
explore: employees {
  label: "Employee Directory & Compensation"
  description: "Employee records with restricted payroll join."

  join: payroll_compensation {
    type: left_outer
    relationship: one_to_one
    sql_on: ${employees.employee_id} = ${payroll_compensation.employee_id} ;;
    required_access_grants: [can_view_payroll]
  }
}
```

### Field-Level Security Inside a Shared View

```lookml
view: employees {
  sql_table_name: `project.hr.employees` ;;

  dimension: employee_id {
    primary_key: yes
    type: number
    sql: ${TABLE}.employee_id ;;
    description: "Unique employee identifier."
  }

  dimension: department_name {
    type: string
    sql: ${TABLE}.department_name ;;
    description: "Department where the employee works."
  }

  dimension: base_salary {
    type: number
    sql: ${TABLE}.base_salary ;;
    value_format_name: usd
    required_access_grants: [can_view_payroll]
    description: "Annual base salary (restricted to HR, Finance, and Executive roles)."
  }

  measure: total_payroll_spend {
    type: sum
    sql: ${base_salary} ;;
    value_format_name: usd
    required_access_grants: [can_view_payroll]
    description: "Sum of annual base salaries (restricted to authorized roles)."
  }
}
```
