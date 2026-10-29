# Looker Architect Developer & Prompt Guide

This human-facing guide accompanies [SKILL.md](../SKILL.md) inside `plugins/looker-lookml-modeling/skills/looker-architect/` and summarizes operating modes, architectural standards, and copy-pasteable prompts.

---

## 1. Core Capabilities & Operating Modes

### Mode A: Greenfield Project Bootstrapping
Scaffolds a complete, modular LookML repository directly via Looker MCP or workspace file tools using the portable templates in [templates.md](templates.md):
- Parameterized `manifest.lkml` (`CONNECTION_NAME`, `DATASET_NAME`, and reusable JSON visual drill constants).
- Clean `<project>.model.lkml` containing only connection constants, ETL-aligned `datagroup` caching, and modular `include:` statements.
- Strict 1:1 physical column mappings in `views/raw/` (`primary_key: yes` first, zero measures).
- Layered business refinements in `views/refined/` (`view: +<view>`) enforcing functional field sequencing (`Keys -> Dimensions -> Measures -> Filters & Parameters -> Sets`), Period-over-Period (PoP) KPI comparisons ([pop_engine.md](pop_engine.md)), and custom visual drill links ([visual_drilling.md](visual_drilling.md)).
- Modular `explores/*.explore.lkml`, primary-key uniqueness tests in `tests/*.test.lkml` ([testing_suite.md](testing_suite.md)), and native tabbed `.dashboard.lookml` layouts ([dashboard_standards.md](dashboard_standards.md)).

### Mode B: Brownfield Audit & Legacy Modernization
Audits and surgically upgrades existing LookML repositories without full-file rewrites:
- Splits monolithic views into `views/raw/` and `views/refined/` while preserving developer comments.
- Re-sequences fields into `Keys -> Dimensions -> Measures -> Filters & Parameters -> Sets`.
- Converts raw SQL aggregates inside `type: number` to native Looker aggregation types (`sum`, `average`, `count`) and wraps ratios in `SAFE_DIVIDE` or `NULLIF(den, 0)` ([modeling_standards.md](modeling_standards.md)).
- Replaces legacy HTML navigation tiles with native Looker `tabs:` (`row: 0, col: 0` per tab) and upgrades KPI `single_value` cards to two-measure PoP comparisons.
- Executes the MCP Self-Healing SQL Loop ([sql_runtime_debugging.md](sql_runtime_debugging.md)) to catch and repair live database execution errors.

---

## 2. Self-Healing SQL Verification Flow

LookML compilation (`validate_project` or `looker-cli project validate`) verifies LookML syntax, not warehouse SQL execution. The self-healing loop validates every dashboard tile against the live connection:

```text
[LookML Compiles] -> [MCP: run_dashboard / query] -> [Fails?] -> [MCP: get_connection_table_columns] -> [Surgical LookML Edit] -> [Re-validate & Re-run (max 5 tries/tile)] -> [Verified HTTP 200]
```

---

## 3. Example Prompts

### Greenfield Bootstrapping
```text
Bootstrap a greenfield LookML project named 'stripe_analytics' for BigQuery using connection 'stripe_prod', dataset 'stripe_raw', and base tables 'charges' and 'refunds'. Follow raw/refined view separation, configure visual drill constants in manifest.lkml with empty drill_fields on core measures, implement the single-explore PoP engine, add primary-key uniqueness tests, and create a native 2-tab LookML dashboard.
```

### Read-Only Architectural Compliance Audit
```text
Run a read-only architectural compliance audit on Looker project 'ecommerce_prod'. Check raw/refined separation, field sequencing, manifest constants, native measure aggregations, value formatting, PK unit tests, native dashboard tabs, and two-measure PoP KPI scorecards. Do not modify any files; produce a prioritized remediation report.
```

### Brownfield Surgical Modernization & Self-Healing QA
```text
Switch to Developer Mode on branch 'refactor/modular-architecture' and modernize Looker project 'ops_observability'. Surgically split monolithic views into views/raw/ and views/refined/, convert HTML dashboard nav bars to native tabs, upgrade single_value KPI cards to PoP comparisons, validate compilation, and run the MCP Self-Healing SQL Loop across all dashboard tiles. Ask before deploying to production.
```
