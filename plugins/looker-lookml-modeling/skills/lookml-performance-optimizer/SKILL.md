---
name: lookml-performance-optimizer
description: >-
  Audits, diagnoses, and optimizes SQL query execution speed, warehouse compute
  cost, datagroup caching, and Persistent Derived Table (PDT) materialization in
  LookML projects. Enforces ETL-aligned datagroups, incremental PDT cold-start
  caps, SARGable dimensions, join pruning, and EXPLAIN plan profiling. Use when
  debugging slow Looker dashboards or Explores, eliminating unnecessary
  Symmetric Aggregations, configuring PDT partitioning or clustering, or aligning
  cache policies with warehouse loads. Do not use for Conversational Analytics
  (CA) agent reasoning-trace loops, system instructions, or golden query tuning
  (use looker-ca-agent-optimize), greenfield LookML project scaffolding (use
  looker-architect), general LookML construct syntax (use lookml-author), or
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

# LookML Performance Optimizer

This skill governs query performance diagnostics, datagroup cache alignment, Persistent Derived Table (PDT) materialization, and SARGable semantic refactoring across LookML projects without altering business metric semantics.

## Prerequisite & Behavioral Guardrails

If the Looker MCP tools or Looker CLI are unavailable, ask the user to install looker-base first.

1. **Reality Mapping (Evidence Before Optimization):** Never guess join cardinalities, table row counts, partition keys, or SQL bottlenecks. Before proposing LookML changes, obtain the target Dashboard ID, Query ID/Slug, Explore, or LookML snippet -- or inspect the active project and warehouse metadata via Looker MCP (`get_project_files`, `get_project_file`, `query`, `query_sql`, `get_connection_table_columns`).
2. **Surgical Modification (No Full-File Rewrites):** Read the target file first (`get_project_file`) and modify only the targeted `datagroup`, `persist_with`, `derived_table`, `join`, or `dimension` blocks while preserving all unrelated fields, includes, and developer comments verbatim (`update_project_file` or localized edits). Never regenerate entire LookML files from scratch.
3. **Developer Mode & Production Safety Gate:** Always switch to Developer Mode (`dev_mode` with `{"devMode": true}` or `looker-cli session update dev`) on a development branch before editing files. Validate LookML compilation (`validate_project` or `looker-cli project validate`), verify query deltas, and request explicit user confirmation before deploying to production (`looker-cli project deploy`).

## Operating Modes

### Mode A: Performance-by-Design (Preventative Engineering)
Apply when adding new Explores, joins, or PDTs to a LookML project:
1. **Verified Join Cardinalities:** Confirm key uniqueness on the "one" side before declaring `many_to_one` or `one_to_one` so Looker neither omits needed Symmetric Aggregations nor injects redundant `SUM(DISTINCT ...)` hashes ([query_diagnostic.md](references/query_diagnostic.md)).
2. **Physical PDT Optimization:** Declare dialect-appropriate LookML partitioning and clustering/indexing (`partition_keys`, `cluster_keys`, or `create_process` DDL indexes) aligned with common dashboard filters ([pdt_optimization.md](references/pdt_optimization.md)).
3. **Centralized ETL Datagroups:** Bind every Explore to a model-level `datagroup` via `persist_with:` backed by a lightweight metadata `sql_trigger` and `max_cache_age` fallback ([caching_datagroups.md](references/caching_datagroups.md)).

### Mode B: Active Performance Tuning (Reactive 6-Step Pipeline)
Apply when diagnosing slow dashboards, Explores, high warehouse slot/byte consumption, or failing PDT builds:
1. **Baseline Measurement:** Enter Developer Mode, inspect target dashboard tiles or queries (`run_dashboard`, `query`, `query_sql`), and record baseline runtime, generated SQL, and bytes/slots scanned.
2. **Parallel SQL & EXPLAIN Profiling:** For multi-tile dashboards, delegate one SQL Profiler subagent per slow tile/Explore following [query_diagnostic.md](references/query_diagnostic.md) to inspect `EXPLAIN` plans, test join-key uniqueness when `_distinct` Symmetric Aggregations appear, and return a pruned bottleneck summary (offending SQL fragment, root cause, LookML remediation).
3. **Caching & Refresh Alignment:** Replace ad-hoc `persist_for` timers and expensive `SELECT MAX(...)` scans on unpartitioned fact tables with zero/low-cost warehouse metadata `sql_trigger` queries per [caching_datagroups.md](references/caching_datagroups.md).
4. **PDT Materialization & Cold-Start Protection:** Evaluate candidate transformations against the 4-Quadrant PDT Decision Matrix below and configure `increment_key`, `increment_offset`, `{% incrementcondition %}`, and the 2-phase Cold-Start Date Cap protocol in [pdt_optimization.md](references/pdt_optimization.md).
5. **Semantic Layer Refactoring:** Refactor giant Explores, add `required_joins` for multi-hop leaf tables, convert non-SARGable filter dimensions (`LOWER()`, `CAST()`, `TRIM()` on raw columns), and replace Liquid `CASE WHEN` loops with physical lookup joins per [lookml_refactoring.md](references/lookml_refactoring.md).
6. **Validation & Delta Verification:** Run `validate_project` (or `looker-cli project validate`), re-execute the baseline queries to confirm identical business results with lower latency/scan cost, and pause for human approval before production deployment.

## Core Optimization Decision Rules

### 1. The 4-Quadrant PDT Decision Matrix
Evaluate all four dimensions before materializing a query into a PDT (details in [pdt_optimization.md](references/pdt_optimization.md)):

| Dimension | Materialize as Incremental / Standard PDT | Keep as Live Explore Query |
| :--- | :--- | :--- |
| **Query Complexity** | Heavy regex, window functions, or multi-stage joins (`> 10s` runtime) | Simple predicates and indexed joins (`< 3s` runtime) |
| **Concurrency** | High-traffic executive dashboards opened repeatedly daily | Sporadic ad-hoc analyst exploration |
| **Freshness SLA** | Hourly, daily, or batch-ETL latency acceptable | Sub-minute / real-time freshness required |
| **Source Scale** | Large (`> 50M` rows) or unpartitioned raw tables | Small (`< 10M` rows), partitioned/indexed tables |

- **Cold-Start Guardrail:** On massive historical tables, pair Looker's mandatory `{% incrementcondition %} <col> {% endincrementcondition %}` tag with a temporary Phase 1 static 30-day `WHERE` cap (plus a matching `dimension` / `dimension_group` in the view), backfill history in warehouse batches, or offload ultra-large transformations to dbt / warehouse materialized views.

### 2. Caching, Join & SARGability Prohibitions
- **No Ad-Hoc `persist_for` in Production:** Always use centralized model `datagroup` policies (`persist_with:`). Never run `SELECT MAX(ts)` every 5 minutes on unpartitioned fact tables; query catalog metadata (`__TABLES__`, `INFORMATION_SCHEMA.TABLES`, or an ETL status table).
- **Never Blindly Flip `one_to_many` to `many_to_one`:** Verify key uniqueness per [query_diagnostic.md](references/query_diagnostic.md) first; if duplicates exist, pre-aggregate the "many" side in a derived table rather than corrupting metrics.
- **No Non-SARGable Wrappers or Liquid `CASE` Loops:** Avoid wrapping filtered columns in `LOWER()`, `TRIM()`, or `CAST()` inside `sql:` and replace Liquid mapping loops with joined lookup tables ([lookml_refactoring.md](references/lookml_refactoring.md)).

## Diagnostics Tooling & Reference Library

| Diagnostic Action | Preferred Looker MCP Tool | Looker CLI Fallback |
| :--- | :--- | :--- |
| Fetch SQL / Run Baseline | `query_sql` (`model`, `explore`, `fields`), `query`, `run_dashboard` | `looker-cli api query query <id> --fields sql` |
| Inspect Warehouse Columns | `get_connection_table_columns`, `get_connection_tables` | `looker-cli api metadata connection_columns <conn>` |
| Read / Patch LookML | `get_project_files`, `get_project_file`, `update_project_file` | `looker-cli project checkout <id> <branch>` |
| Validate LookML Syntax | `validate_project` (`{"project_id": "<id>"}`) | `looker-cli project validate <id>` |
| Inspect Usage & Instance Health | `health_analyze`, `health_pulse` | `looker-cli health pulse` |

- **SQL Profiling, EXPLAIN Plans & Symmetric Aggregation Uniqueness Audit:** [query_diagnostic.md](references/query_diagnostic.md)
- **Centralized Datagroups, Catalog Triggers & Cache Warming:** [caching_datagroups.md](references/caching_datagroups.md)
- **PDT Decision Matrix, Partitioning/Clustering & Cold-Start Protocol:** [pdt_optimization.md](references/pdt_optimization.md)
- **Join Pruning, `required_joins` & SARGable LookML Refactoring:** [lookml_refactoring.md](references/lookml_refactoring.md)
- **Architecture Overview & 7-Step Workflow Guide:** [guide.md](references/guide.md)
