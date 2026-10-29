---
name: looker-architect
description: >-
  Architects, scaffolds, audits, and refactors multi-layer enterprise LookML
  projects across greenfield and brownfield repositories. Enforces raw-and-refined
  view separation, functional field sequencing, Period-over-Period KPI engines,
  custom visual drilling, native tabbed LookML dashboards, primary-key unit
  tests, and MCP self-healing SQL verification. Use when bootstrapping a new
  LookML project from scratch, modernizing a legacy LookML repository structure,
  or running a full architectural compliance audit. Do not use for authoring
  isolated single-construct LookML snippets (use lookml-author), tuning slow SQL
  queries, datagroups, or PDT builds (use lookml-performance-optimizer), PR diff
  reviews (use lookml-reviewer), Conversational Analytics agent creation or
  optimization (use looker-ca-agent-create or looker-ca-agent-optimize), or
  instance-wide System Activity health, governance, and unused content audits
  (use looker-audit).
compatibility: Requires looker-base (Looker MCP and looker-cli).
license: Apache-2.0
metadata:
  version: 0.1.0
  usage-interface: looker-mcp looker-cli
  domain: looker-lookml-modeling
  status: preview
  publisher: google
---

# Looker Architect

This skill governs end-to-end architecture, scaffolding, brownfield modernization, compilation verification, and runtime SQL validation for modular, dialect-agnostic LookML projects.

## Prerequisite & Behavioral Guardrails

If the Looker MCP tools or Looker CLI are unavailable, ask the user to install looker-base first.

1. **Reality Mapping & Completeness Checklist (Context First):** Never guess connection names, datasets, SQL dialects, or column schemas. Before generating or refactoring LookML, inspect live files and schemas via Looker MCP (`get_project_files`, `get_project_file`, `get_connection_tables`, `get_connection_table_columns`) or ask the user for missing project ID, connection, dataset/schema, dialect, and base tables. Compile an explicit **Completeness Checklist** covering 100% of required views, explores, KPIs, and dashboard tabs -- never apply PoP, formatting, or visual drills selectively to only a subset of views.
2. **Surgical Modification (No Full-File Rewrites):** When refactoring or repairing existing LookML or dashboard files, first read the file (`get_project_file`) and modify only the targeted blocks while preserving all unrelated fields, joins, includes, and developer comments verbatim (`update_project_file` or localized edits). Never regenerate existing files from scratch.
3. **Developer Mode & Production Safety Gate:** Always activate Developer Mode (`dev_mode` with `{"devMode": true}` or `looker-cli session update dev`) on a development branch before modifying files. Validate LookML compilation and tests (`validate_project`, `run_lookml_tests`, or `looker-cli project validate`) and obtain explicit user approval before merging to `main` or running `looker-cli project deploy`.

## Operating Modes

### Mode A: Greenfield Project Architecture (8-Step Workflow)
1. **Schema & Requirement Discovery:** Introspect warehouse tables (`get_connection_tables`, `get_connection_table_columns`), clarify target KPIs/audiences, and write the Completeness Checklist.
2. **Workspace Initialization:** Switch to Developer Mode and align the project directory name with the target Looker `project_id`.
3. **Modular Scaffolding:** Generate the canonical directory tree (`views/raw/`, `views/refined/`, `explores/`, `tests/`, `dashboards/`, `<project>.model.lkml`, `manifest.lkml`) directly from the portable patterns in [templates.md](references/templates.md).
4. **Raw & Refined Layering:** Map physical columns 1:1 in `views/raw/` (`primary_key: yes` first, zero business logic) and layer refinements (`view: +view_name`) in `views/refined/` per [consumption_guide.md](references/consumption_guide.md) and [modeling_standards.md](references/modeling_standards.md).
5. **Advanced Analytics & Dashboards:** Implement the single-explore PoP engine ([pop_engine.md](references/pop_engine.md)), manifest-backed visual drill links ([visual_drilling.md](references/visual_drilling.md)), aggregate rollups if needed ([aggregate_awareness.md](references/aggregate_awareness.md)), and native tabbed `.dashboard.lookml` layouts ([dashboard_standards.md](references/dashboard_standards.md)). For large multi-tab dashboards, delegate one subagent per tab (each starting at `row: 0, col: 0`) and merge into `elements`.
6. **Automated LookML Data Tests:** Create `tests/<explore>.test.lkml` suites verifying primary-key uniqueness and business logic boundaries ([testing_suite.md](references/testing_suite.md)).
7. **Compiler & Runtime SQL Verification:** Run `validate_project` and `run_lookml_tests`, then execute dashboard queries via the MCP Self-Healing SQL Loop ([sql_runtime_debugging.md](references/sql_runtime_debugging.md)).
8. **Documentation & Controlled Deployment:** Generate project root `README.md` from [templates.md](references/templates.md) and pause for explicit human approval before production deployment.

### Mode B: Brownfield Audit & Modernization
1. **Inventory & Deviation Audit:** Inspect existing `.model.lkml`, views, explores, tests, and dashboards (`get_project_files`, `get_project_file`) against the 11 Architectural Golden Rules below. If the user requested a read-only audit, output a structured compliance scorecard without modifying files.
2. **Surgical Refactoring:** Delegate localized file updates to split monolithic views into `views/raw/` and `views/refined/`, enforce field sequencing, convert raw SQL aggregates to native measure types with `NULLIF`/`SAFE_DIVIDE`, add manifest visual drills (`drill_fields: []`), convert HTML nav bars to native `tabs:`, and upgrade KPI `single_value` cards to two-measure PoP comparisons.
3. **Compiler Gate & Self-Healing SQL Loop:** Verify zero LookML compiler errors (`validate_project` / `looker-cli project validate`), then run `run_dashboard` or `query` per tile and repair dialect/schema mismatches via [sql_runtime_debugging.md](references/sql_runtime_debugging.md) (capped at 5 attempts per failing tile).

## Architectural Golden Rules (Summary)

Full LookML syntax patterns and anti-patterns for all 11 rules are in [modeling_standards.md](references/modeling_standards.md):

1. **Centralized Constants:** Parameterize `CONNECTION_NAME` and `DATASET_NAME` in `manifest.lkml` with `export: override_optional`; never hardcode them in models or views.
2. **Visual Drill Library:** Define reusable chart JSON constants in `manifest.lkml`; set `drill_fields: []` on every core measure to enable custom `link` blocks ([visual_drilling.md](references/visual_drilling.md)).
3. **Raw vs. Refined Separation:** Keep `views/raw/` strictly 1:1 with physical columns (`primary_key: yes` first); put measures, labels, descriptions, drills, and PoP logic in `views/refined/*_rfn.view.lkml`.
4. **Functional Field Sequencing:** Order refined views strictly top-to-bottom: `1. Keys -> 2. Dimensions -> 3. Measures -> 4. Filters & Parameters -> 5. Sets` (sorted A-Z or by `group_label`).
5. **Substitution Inheritance:** Reference `${field_name}` rather than `${TABLE}.column` in measures and derived fields.
6. **Native Aggregations:** Use native Looker measure types (`sum`, `average`, `count`, `count_distinct`) instead of raw SQL `SUM()`/`AVG()` inside `type: number` to preserve Symmetric Aggregations.
7. **Naming & Suffixes:** Use `snake_case` for all files/identifiers and standard measure suffixes (`_count`, `_total`, `_amount`).
8. **Safe Math & Mandatory Formatting:** Protect divisions with `SAFE_DIVIDE` or `NULLIF(den, 0)`, compute ratios over aggregated measures (never `type: average` on row ratios), and set `value_format_name` or `value_format` on 100% of numeric measures.
9. **Modular Explores & Join Pruning:** Place one explore per file in `explores/*.explore.lkml`; keep `.model.lkml` restricted to `connection`, `datagroup`, `persist_with`, and `include` statements.
10. **Native Tabbed Dashboards & PoP Scorecards:** Use `layout: newspaper` and native `tabs:` (never HTML nav menus), reset each tab at `row: 0, col: 0`, and configure KPI `single_value` cards with current + change PoP measures mapped to `pop_date_filter`.
11. **Zero Dummy Calculations:** Never write static mock values (`sql: 0.05 ;;`); every measure must compute dynamic warehouse SQL.

## Tooling & Reference Library

| Lifecycle Action | Preferred Looker MCP Tool | Looker CLI Fallback |
| :--- | :--- | :--- |
| Enter Developer Mode | `dev_mode` (`{"devMode": true}`) | `looker-cli session update dev` |
| Introspect Warehouse Schema | `get_connection_tables`, `get_connection_table_columns` | `looker-cli api metadata connection_columns <conn>` |
| Read / Write Project Files | `get_project_files`, `get_project_file`, `create_project_file`, `update_project_file` | `looker-cli project checkout <id> <branch>` |
| Validate LookML & Data Tests | `validate_project`, `run_lookml_tests` | `looker-cli project validate <id>` |
| Inspect Explore Usage Telemetry | `health_analyze` (`action: "projects" \| "models" \| "explores"`) | `looker-cli health analyze` |
| Execute & Audit Dashboards | `get_dashboards`, `run_dashboard`, `query`, `query_sql` | `looker-cli api dashboard dashboard_lookml <id>` |
| Deploy (User Approval Required) | -- | `looker-cli project deploy <id>` |

- **Core LookML Golden Rules & Code Patterns:** [modeling_standards.md](references/modeling_standards.md)
- **Portable Project Scaffolding Templates:** [templates.md](references/templates.md)
- **Layered Refinements Guide:** [consumption_guide.md](references/consumption_guide.md)
- **Dialect-Agnostic Period-over-Period Engine:** [pop_engine.md](references/pop_engine.md)
- **Manifest Visual Drilling Library:** [visual_drilling.md](references/visual_drilling.md)
- **Native Tabbed LookML Dashboard Standards:** [dashboard_standards.md](references/dashboard_standards.md)
- **Primary Key & Business Unit Testing:** [testing_suite.md](references/testing_suite.md)
- **Aggregate Tables & `_in_query` Routing:** [aggregate_awareness.md](references/aggregate_awareness.md)
- **MCP Self-Healing Runtime SQL Loop:** [sql_runtime_debugging.md](references/sql_runtime_debugging.md)
- **Human Developer & Prompt Guide:** [guide.md](references/guide.md)
