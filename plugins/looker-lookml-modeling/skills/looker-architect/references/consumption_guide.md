# LookML Refinements & Layered Project Architecture

This reference details how to extend base physical schemas using **LookML Refinements** (`view: +<view_name>` and `explore: +<explore_name>`) without modifying auto-generated raw views. For canonical `manifest.lkml` and `<project_name>.model.lkml` scaffolding, see [templates.md](templates.md).

---

## 1. Raw-to-Refined Include Chain

Because `<project_name>.model.lkml` at the repository root includes `/views/refined/*.view.lkml` (and does not directly include `/views/raw/*.view.lkml`), every refined view file **must** explicitly `include:` its corresponding raw view at the top of the file:

```text
views/raw/users.view.lkml  <-- included by --  views/refined/users_rfn.view.lkml  <-- included by --  <project_name>.model.lkml
```

---

## 2. Layering View Customizations (`view: +<view_name>`)

Keep `views/raw/<table_name>.view.lkml` strictly 1:1 with physical database columns (`primary_key: yes` first, zero measures). Layer business dimensions, label overrides, measures, PoP filters, and drill sets inside `views/refined/<table_name>_rfn.view.lkml`:

```lookml
include: "/views/raw/users.view.lkml"

view: +users {
  # ==================== 1. KEYS ====================
  dimension: id {
    primary_key: yes
    hidden: yes
  }

  # ==================== 2. DIMENSIONS ====================
  dimension: corporate_segment {
    label: "Corporate Segment"
    group_label: "Corporate Details"
    description: "Corporate classification derived from email domain."
    type: string
    sql:
      CASE
        WHEN ${email} LIKE '%@enterprise.com' THEN 'Enterprise'
        ELSE 'Retail'
      END ;;
  }

  dimension: name {
    label: "Customer Full Name"
    description: "Full display name overriding the raw column label."
  }

  # ==================== 3. MEASURES ====================
  measure: users_count {
    label: "Total Users"
    description: "Distinct count of registered users."
    type: count
    value_format_name: decimal_0
    drill_fields: [default_drill*]
  }

  # ==================== 5. SETS ====================
  set: default_drill {
    fields: [id, name, corporate_segment, created_date]
  }
}
```

---

## 3. Layering Explore Refinements (`explore: +<explore_name>`)

Use `explore: +<explore_name>` when layering environment-specific `access_filter` rules or aggregate tables onto a base Explore in `explores/<explore_name>.explore.lkml` without rewriting its core `join:` definitions:

```lookml
include: "/explores/orders.explore.lkml"

explore: +orders {
  access_filter: {
    field: users.corporate_segment
    user_attribute: allowed_segment
  }
}
```

---

## 4. Refinement Rules Checklist
1. **Explicit Raw Include:** Always start `views/refined/<name>_rfn.view.lkml` with `include: "/views/raw/<name>.view.lkml"`.
2. **Plus (`+`) Prefix:** Prefix refined blocks with `+` (`view: +users`); omitting `+` triggers duplicate-view compiler errors.
3. **Additive Dimension Timeframes:** Refining a `dimension_group` overrides its `timeframes:` array rather than appending; list the complete desired timeframe array in the refinement.
4. **Preserve Raw Purity:** Never place measures, `html:` formatting, or `link:` blocks inside `views/raw/`.
