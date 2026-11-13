# LookML Style Guide & Modeling Best Practices

This canonical shared reference defines the foundational style, naming, structural, and governance rules for authoring and reviewing LookML across models, Explores, views, and fields.

---

## 1. Naming & Uniqueness Conventions

All LookML object identifiers (`model`, `explore`, `view`, `dimension`, `dimension_group`, `measure`, `filter`, `parameter`, `set`, `datagroup`, `access_grant`) must use `lowercase_snake_case`. Use the `label` parameter when custom UI capitalization or punctuation is needed.

### Uniqueness Scopes
- **Model (`*.model.lkml`):** Instance-wide uniqueness required (prevents URL collisions and routing conflicts).
- **View (`*.view.lkml`):** Project-wide uniqueness required (acts as the namespace for its fields).
- **Explore (`*.explore.lkml`):** Model-wide uniqueness required (query entry point).
- **Field & Set:** View-wide uniqueness required.

### Field Naming Rules
- **Booleans (`type: yesno`):** Prefix with `is_` or `has_` (e.g., `is_active`, `has_churned`).
- **Time Dimension Groups (`type: time`):** Never include `_date`, `_time`, or `_at` in the `dimension_group` name. Looker appends the timeframe automatically (`dimension_group: created` -> `created_date`, `created_month`).
- **Duration Dimension Groups (`type: duration`):** Never include the word `duration` in the group name (`dimension_group: since_signup` with `intervals: [day, month]` -> `days_since_signup`, `months_since_signup`).
- **Measures:** Prefix counts with `count_` (`count_orders`), sums with `total_` (`total_revenue`), and averages with `avg_` (`avg_order_value`).

---

## 2. Model Standards (`*.model.lkml`)

- **Granular `include` Paths (Do Not Use Broad Wildcards):**
  - **Do:** Use explicit or domain-scoped includes (`include: "/views/users.view.lkml"`, `include: "/explores/orders.explore.lkml"`).
  - **Don't:** Avoid recursive or project-wide wildcards (`include: "/**/*.view.lkml"` or `include: "*.view.lkml"`), which cause namespace collisions and slow down LookML validation.
- **Datagroups over `persist_for`:**
  - **Do:** Align Explore caching and Persistent Derived Table (PDT) rebuilds with upstream ETL/ELT pipelines using `datagroup:` (`sql_trigger` + `max_cache_age`) and `persist_with:`.
  - **Don't:** Avoid scattered `persist_for` timers except on real-time operational Explores (< 1 hour).

---

## 3. Explore & Join Standards (`*.explore.lkml`)

- **100% Description & Label Coverage:** Every Explore must define a clear `description` and user-friendly `label`.
- **Focused Explores & One Explore Per File:** Prefer small, purpose-built Explores in dedicated `explores/<name>.explore.lkml` files over monolithic Explores with dozens of joins.
- **Explicit Join `relationship` & `sql_on`:**
  - **Do:** Explicitly declare `relationship:` (`many_to_one`, `one_to_one`, `one_to_many`, `many_to_many`) and `sql_on:` using LookML substitution syntax (`${left_view.key} = ${right_view.key} ;;`) on every join so Looker computes symmetric aggregates accurately.
  - **Do:** Prefer `type: left_outer` joins by default to avoid unintentionally dropping base table rows.
- **`view_label` vs. `from`:**
  - **Don't:** Never use `from:` merely to change how a joined view is labeled in the UI—use `view_label:` instead.
  - **Do:** Reserve `from:` strictly for role-playing/polymorphic joins (joining `users` twice as `buyers` and `sellers`), self-joins, or rescoping extended views.
- **Join on `raw` Timeframes:**
  - **Don't:** Never join on formatted date/time dimensions (which inject timezone conversions and string casts into `ON` predicates). Always join on the `raw` timeframe (`${events.created_raw} = ${calendar.date_raw}`).

---

## 4. View & Field Standards (`*.view.lkml`)

- **Mandatory Primary Key (`primary_key: yes`):**
  - Every view representing a table, Native Derived Table (NDT), or SQL Derived Table (SDT) **must** define a unique primary key as its first dimension with `primary_key: yes`. For composite keys, concatenate the component columns into a single `primary_key: yes` dimension.
  - Hide raw technical primary keys and foreign keys (`hidden: yes`) unless business users directly search or filter by those IDs.
- **Explicit `sql_table_name`:** Always specify `sql_table_name` explicitly on standard views rather than relying on implicit view-name defaults.
- **Measure Field References (Single Source of Truth):**
  - **Do:** Reference LookML dimensions inside measures (`sql: ${sale_price} ;;`).
  - **Don't:** Never reference raw `${TABLE}.column_name` directly inside aggregated measures when a dimension exists.
- **100% Field Documentation:** Every non-hidden dimension, dimension group, measure, filter, and parameter must include a human-readable `description`.
- **Duration Dimension Groups for Date Diffs:** Always use `dimension_group` with `type: duration` (`intervals`, `sql_start`, `sql_end`) instead of writing custom `DATEDIFF` / `DATE_DIFF` SQL inside a standard `dimension`.
- **Evaluate NDTs Before SDTs:** When creating entity rollups or summary fact tables, prefer Native Derived Tables (`explore_source`) over raw SQL Derived Tables (`sql`) to inherit Row-Level Security and prevent code drift.

---

## 5. Modularity & Authoring Guardrails

- **DRY Principles (`extends`, `+refinements`, `set:`):**
  - Use **Refinements (`+view_name`)** to layer modifications onto existing views/Explores without renaming (e.g., raw-to-refined layering, Hub & Spoke, or Marketplace Blocks).
  - Use **Extensions (`extends: [base_view]`)** to create a new specialized view/Explore variant while keeping the original object intact.
  - Use **Sets (`set: detail`)** for reusable `drill_fields` and Explore `fields:` curation.
- **Surgical Application Scope:** When modifying an existing project, apply changes strictly to the files and constructs required by the user's request. Do not refactor unrelated legacy code unless explicitly asked.
- **Zero-Error Validation Policy:** Never consider a LookML authoring task complete until `validate_project` passes with zero errors on the modified files.
