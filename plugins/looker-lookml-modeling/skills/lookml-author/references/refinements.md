# LookML Includes, Refinements (`+`) & Project Layering

This reference covers LookML `include` scoping, object-oriented refinements (`+view` and `+explore`), and the enterprise **One Explore Per File** pattern.

## 1. `include` Scoping Rules

`include` declarations expose LookML views, Explores, tests, and dashboards to the current file:

- `/views/users.view.lkml`: Explicit single-file include (**Preferred**).
- `/views/finance/*.view.lkml`: Domain-scoped folder wildcard (**Good**).
- `//central_hub_project/views/users.view.lkml`: Remote project import (requires `local_dependency` or `remote_dependency` in `manifest.lkml`).
- `/**/*.view.lkml`: Recursive wildcard across all folders (**Avoid**—causes namespace collisions and degrades validation performance).

---

## 2. Refinements (`+`) for Layering

Refinements modify an existing `view:` or `explore:` in place without changing the original file or creating a new object name. Use refinements for:

1. **Raw vs. Refined View Separation:** Keep auto-generated schema columns in `views/raw/users.view.lkml` and layer custom dimensions, measures, and drill sets in `views/refined/users_rfn.view.lkml`.
2. **Hub & Spoke Architecture:** Adapt a central "Hub" model for regional or department "Spoke" teams.
3. **Marketplace Blocks:** Customize read-only vendor blocks without forking upstream files.

### Rules of Engagement for Refinements

- **Include First:** The file containing `view: +users` **must** `include` the base `users.view.lkml` file first.
- **Last Include Wins:** When multiple refinement files modify `+users`, Looker applies them in the exact order they are included.
- **Additive vs. Override:**
  - Declaring a new field adds it to the view.
  - Re-declaring an existing field name merges/overrides only the specified parameters (e.g., adding `description:` or `hidden: yes` to an existing dimension while keeping its original `sql:` and `type:`).
  - List parameters (such as `drill_fields` or `timeframes`) are **replaced** rather than appended—restate the full list when overriding.

---

## 3. The "One Explore Per File" Pattern

For maintainable enterprise projects, isolate each Explore in its own `.explore.lkml` file under `explores/`:

- **Explore File (`explores/orders.explore.lkml`):**
  1. `include` **only** the base and refined views joined in this Explore.
  2. Apply any Explore-specific view refinements (`view: +users`).
  3. Define `explore: orders { ... }`.
- **Model File (`models/ecommerce.model.lkml`):**
  1. Declare `connection:` and `datagroup:` policies.
  2. `include: "/explores/orders.explore.lkml"`.
  3. Keep `explore:` blocks out of `.model.lkml` so developers can work on separate Explores without merge conflicts or global namespace pollution.

---

## 4. Examples

### Raw + Refined View Layering (`views/refined/users_rfn.view.lkml`)

```lookml
include: "/views/raw/users.view.lkml"

view: +users {
  # 1. Enrich an existing raw dimension without repeating its sql: or type:
  dimension: id {
    primary_key: yes
    hidden: yes
    description: "Primary key for the users table."
  }

  dimension: name {
    label: "Customer Full Name"
    description: "Legal full name of the registered customer."
  }

  # 2. Add derived dimensions and measures in the refinement layer
  dimension: email_domain {
    type: string
    sql: SPLIT(${email}, '@')[SAFE_OFFSET(1)] ;;
    description: "Domain portion of the user's email address."
  }

  measure: count_users {
    type: count
    drill_fields: [id, name, email, email_domain]
    description: "Total number of registered users."
  }
}
```

### Explore-Scoped Refinement (`explores/marketing_orders.explore.lkml`)

```lookml
include: "/views/refined/orders_rfn.view.lkml"
include: "/views/refined/users_rfn.view.lkml"

# Layer marketing-specific attribution logic onto users ONLY within this Explore
view: +users {
  dimension: first_touch_channel {
    type: string
    sql: COALESCE(${TABLE}.utm_medium, 'direct') ;;
    description: "First-touch marketing channel for the user."
  }
}

explore: marketing_orders {
  label: "Marketing Orders Attribution"
  description: "Orders joined with user marketing attribution channels."
  view_name: orders

  join: users {
    type: left_outer
    relationship: many_to_one
    sql_on: ${orders.user_id} = ${users.id} ;;
  }
}
```
