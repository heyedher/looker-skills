# LookML Modeling Workflow & CLI Execution Guide

This reference covers LookML requirement analysis, CLI/MCP discovery commands, view creation, and the iterative validation and testing loop. *(For naming, formatting, and architectural rules, see [lookml-style-guide.md](lookml-style-guide.md).)*

## 1. Analyzing Requirements & LookML File Types

Before writing or editing LookML, map the user's business question to the existing project structure:

1. **Understand the Request:** Identify the target entities, grain, metrics, and filters needed.
2. **Search Existing Resources First:** Inspect the project's existing models, Explores, views, dimensions, and measures. **Never recreate existing logic**—reuse existing dimensions, measures, and sets whenever possible.
3. **Determine Required File Types:**
   - **`manifest.lkml`**: Project-level settings, constants, and remote project imports.
   - **`*.model.lkml`**: Connection mapping, datagroup caching policies, and Explore includes.
   - **`explores/*.explore.lkml`**: Explore definitions and join relationships.
   - **`views/*.view.lkml`**: Dimensions, dimension groups, measures, sets, and derived tables.
   - **`tests/*.test.lkml`**: Automated `test:` assertions verifying primary key uniqueness and business logic.
   - **`dashboards/*.dashboard.lookml`**: Version-controlled LookML dashboards.

---

## 2. Discovery & Exploration Commands (`looker-cli` / Looker MCP)

### Project & Semantic Model Discovery
- **List projects:** `looker-cli api project all_projects` (MCP: `get_projects`)
- **List models:** `looker-cli api lookmlmodel all_lookml_models` (MCP: `get_models`)
- **Inspect model:** `looker-cli api lookmlmodel lookml_model {model_name}` (MCP: `get_explores`)
- **Inspect Explore fields (preferred over reading raw view files):**
  ```bash
  looker-cli api lookmlmodel lookml_model_explore {model_name} {explore_name}
  ```
  *(MCP: `get_dimensions`, `get_measures`, `get_filters`, `get_parameters`)*

### Database Schema Discovery
- **List connections:** `looker-cli connection ls` (MCP: `get_connections`)
- **List schemas:** `looker-cli api metadata connection_schemas {connection_name}` (MCP: `get_connection_schemas`)
- **List tables:** `looker-cli api metadata connection_tables {connection_name}` (MCP: `get_connection_tables`)
- **List table columns:**
  ```bash
  looker-cli api metadata connection_columns {connection_name} --schema_name {schema_name} --table_names {table_name}
  ```
  *(MCP: `get_connection_table_columns`)*

### Query & SQL Inspection
- **Run saved query:** `looker-cli query runquery {query_id}`
- **Run inline query / inspect generated SQL:** `looker-cli api query run_inline_query` (MCP: `query` and `query_sql`). Always use fully qualified `view.field` names.

---

## 3. Creating & Updating LookML Files via CLI

When using `looker-cli` (which does not have an auto-generator subcommand for views), construct the LookML view definition from the database column schema retrieved in Section 2, write it to a temporary file, and upload it to the active development workspace:

```bash
# 1. Ensure session is in dev mode
looker-cli session update --workspace-id dev

# 2. Upload new or updated LookML file
looker-cli project file create {project_id} views/{view_name}.view.lkml /tmp/{view_name}.view.lkml
```
*(When using Looker MCP, toggle `dev_mode` to `true` and use `create_view_from_table`, `create_project_file`, or `update_project_file`.)*

---

## 4. Validation & Verification Feedback Loop

After every LookML edit, execute the following verification loop:

1. **Run the LookML Validator:**
   ```bash
   looker-cli api project validate_project {project_id}
   ```
   *(MCP: `validate_project`)*
2. **Fix New Errors Iteratively:** If validation reports syntax, type, or reference errors in your modified code, resolve them and re-run validation until zero errors remain. (Keep validation scoped to your changes; do not refactor unrelated pre-existing project errors unless requested.)
3. **Execute LookML Data Tests:**
   ```bash
   looker-cli api project all_lookml_tests {project_id}
   looker-cli api project run_lookml_test {project_id}
   ```
   *(MCP: `get_lookml_tests` and `run_lookml_tests`)*
4. **Verify Generated SQL:** Run a sample inline query (`query_sql` / `run_inline_query`) to confirm the SQL dialect syntax, join predicates, and aggregation results match expectations.
