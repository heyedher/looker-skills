---
name: lookml-author
description: >-
  Author, extend, and modify LookML models, views, explores, fields, derived
  tables, refinements, sets, access grants, Liquid logic, and data tests. Use
  when creating or editing individual LookML files or constructs. Do not use
  for greenfield end-to-end project scaffolding (use looker-architect), LookML
  code review (use lookml-reviewer), SQL dialect migration (use
  lookml-dialect-migration), or query performance tuning (use
  lookml-performance-optimizer).
license: Apache-2.0
compatibility: Requires looker-base (Looker MCP and looker-cli).
metadata:
  version: 1.0.0
  domain: looker-lookml-modeling
  status: ga
  usage-interface: looker-mcp looker-cli
  publisher: google
  shared-refs: lookml-style-guide
---

# LookML Authoring (`lookml-author`)

This skill guides the end-to-end workflow for creating and modifying LookML constructs (models, Explores, views, fields, derived tables, refinements, sets, access grants, Liquid templates, and data tests) with strict reality mapping and surgical precision.

> **Prerequisite:** If the Looker MCP tools or Looker CLI are unavailable, ask the user to install `looker-base` first.

---

## Authoring Workflow

### Phase 1: Reality Mapping & Discovery

Before writing or modifying any LookML code, inspect the live Looker project and database metadata so you never guess table or field names:

1. **Enter Development Mode:** Enable `dev_mode` (`true`) via Looker MCP or run `looker-cli session update --workspace-id dev`.
2. **Inspect Existing Semantic Assets:**
   - List and inspect models, Explores, and exposed fields (`get_models`, `get_explores`, `get_dimensions`, `get_measures`, `get_project_files`, or `looker-cli api lookmlmodel lookml_model_explore`).
   - **Reuse Before Creating:** Check whether existing dimensions, measures, sets, or views already satisfy the user's request. Never duplicate existing logic.
3. **Verify Database Schema:** When adding new views or columns, query the connection metadata (`get_connection_tables`, `get_connection_table_columns`, or `looker-cli api metadata connection_columns`) to confirm exact column names and data types.

### Phase 2: Construct Selection & Reference Lookup

Consult the specific reference guide in `references/` matching the LookML construct you are authoring:

| Construct / Task | Reference Guide | Key Standards |
| :--- | :--- | :--- |
| **LookML Style Guide (Shared)** | [references/lookml-style-guide.md](references/lookml-style-guide.md) | Naming conventions, uniqueness scopes, primary keys, joins, and Do's & Don'ts |
| **CLI Discovery & Modeling Loop** | [references/modeling-guidelines.md](references/modeling-guidelines.md) | Requirement analysis, CLI/MCP discovery commands, file upload, and validation loop |
| **Models & Caching (`.model.lkml`)** | [references/model.md](references/model.md) | Connection mapping, granular `include` patterns, and `datagroup` caching |
| **Explores & Joins (`.explore.lkml`)** | [references/explore.md](references/explore.md) | Explicit `relationship` & `sql_on`, aggregate tables, UNNEST, and `access_filter` |
| **Views & Derived Tables (`.view.lkml`)** | [references/view.md](references/view.md) | Explicit `sql_table_name`, `primary_key: yes`, and NDT (`explore_source`) vs. SDT |
| **Fields, Formats & Timeframes** | [references/fields.md](references/fields.md) | Dimensions, measures, `dimension_group` (`time` & `duration`), filters, parameters, and `value_format` |
| **Liquid Variables & Dynamic SQL** | [references/liquid.md](references/liquid.md) | `_in_query` vs. `_is_selected`, `sql_quote`, dynamic joins, and HTML formatting |
| **Includes & Refinements (`+`)** | [references/refinements.md](references/refinements.md) | Layering (`+view`), Hub & Spoke, and One Explore Per File pattern |
| **Field Sets (`set:`)** | [references/sets.md](references/sets.md) | Reusable drill sets (`detail*`), Explore field visibility, and exclusions |
| **Access Grants (`access_grant:`)** | [references/access-grants.md](references/access-grants.md) | Model-level `access_grant` definitions and `required_access_grants` |
| **LookML Data Tests (`test:`)** | [references/tests.md](references/tests.md) | Primary key uniqueness assertions, accuracy checks, and business logic tests |

### Phase 3: Surgical Modification & Core Guardrails

Apply changes using `create_project_file` / `update_project_file` (or `looker-cli project file`) while enforcing these non-negotiable rules:

- **Surgical Scope:** Modify only the files and constructs necessary to fulfill the user prompt. Do not refactor unrelated legacy code unless explicitly asked.
- **Mandatory Primary Keys:** Every view, derived table, and PDT must define a primary key as its first dimension with `primary_key: yes` (essential for symmetric aggregates).
- **100% Description Coverage:** Every new Explore, dimension, and measure must include a clear human-readable `description`.
- **Dimension References over Raw Columns:** Measures must reference LookML dimensions (`${sale_price}`) rather than raw table columns (`${TABLE}.sale_price`).
- **Duration Dimension Groups for Date Diffs:** Always use `dimension_group` with `type: duration` (`intervals`, `sql_start`, `sql_end`) instead of writing custom `DATEDIFF`/`DATE_DIFF` dimensions.
- **Evaluate NDTs Before SDTs:** Prefer Native Derived Tables (`explore_source`) over raw SQL Derived Tables (`sql`) when building entity rollups so Row-Level Security and field definitions are inherited automatically.
- **Granular Includes & Explicit Joins:** Avoid recursive `include: "/**/*.view"` wildcards, and always specify both `relationship` (`many_to_one`, `one_to_one`, etc.) and `sql_on` on every `join`.

### Phase 4: Validation & Verification Feedback Loop

1. **Validate LookML:** Run `validate_project` (or `looker-cli api project validate_project {project_id}`) after every file edit.
2. **Run Data Tests & Sample Queries:** If data tests exist, execute `run_lookml_tests` (or `looker-cli api project run_lookml_test {project_id}`) and run a verification query (`query` / `query_sql`) to confirm the generated SQL and results.
3. **Zero-Error Policy:** Never mark a task complete while LookML validation errors introduced by your changes remain unresolved.
