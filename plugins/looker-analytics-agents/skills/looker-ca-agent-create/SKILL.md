---
name: looker-ca-agent-create
description: >-
  Builds and configures brand-new Looker Conversational Analytics (CA)
  Standalone Agents and Dashboard Agents from scratch. Use when the user asks to
  create, scaffold, or design a new Looker CA agent, author initial 4-part
  XML/YAML system instructions, curate seed golden queries, configure Dashboard
  Agent context, or enrich LookML metadata for a new CA agent deployment. Do not
  use for auditing, diagnosing reasoning traces, or running Side-by-Side (SxS)
  optimizations on an existing CA agent (use looker-ca-agent-optimize).
license: Apache-2.0
compatibility: Requires looker-base (Looker MCP and looker-cli).
metadata:
  version: 0.1.0
  domain: looker-analytics-agents
  status: preview
  usage-interface: looker-mcp looker-cli
  publisher: google
  shared-refs: looker-ca-best-practices lookml-ca-modeling-standards
---

# Looker Conversational Analytics (CA) Agent Creator

## Overview

This skill designs, validates, and deploys production-ready Looker Conversational Analytics (CA) **Standalone Agents** (Explore-backed) and **Dashboard Agents** (Dashboard-backed) from the ground up using the five-step `build_agent` workflow.

If the Looker MCP tools or Looker CLI are unavailable, ask the user to install `looker-base` first.

---

## Agent Architecture Matrix

| Dimension | Standalone Agent | Dashboard Agent |
| :--- | :--- | :--- |
| **Grounding Target** | 1 to 5 curated LookML Explores (`explores`) | Single Looker Dashboard (`dashboard_id` / `slug`) |
| **Primary Use Case** | Multi-Explore ad-hoc Q&A and deep domain exploration | Guided Q&A over executive KPIs, tiles, and filters |
| **Golden Queries** | Supported and recommended (`3-5` seed archetypes, `< 20` cap) | Inherited from Dashboard tiles (`looker_golden_queries` omitted) |
| **Explore Discovery** | Automatic discovery via `get_explores` if omitted | Extracted from Dashboard tile queries via `get_dashboards` |

See [standalone_vs_dashboard_agents.md](references/standalone_vs_dashboard_agents.md) for complete schema differences and selection criteria.

---

## Behavioral Guardrails (Mandatory)

1. **Two Human-in-the-Loop Gates Only:** Prompt the user strictly at **Step 1** (Input Validation) and **Step 5** (Interactive Review of **Plan A: New CA Agent Deployment** and **Plan B: LookML `dev_mode` Enrichments**). Execute Steps 2, 3, and 4 automatically.
2. **Zero Hallucinated Schema References & LookML Refinement Awareness:** Never invent model names, Explore names, field names, or dashboard IDs. Verify every referenced entity via Looker MCP before generating instructions or golden queries. When inspecting `.view.lkml` files, never mistake **LookML Refinements (`view: +view_name` across `raw/` and `refined/` layers)** for duplicate fields, and never propose destructive LookML edits that could break existing Explores or dashboards.
3. **Safe Deployment & Dev-Branch Isolation:** Never create or mutate an agent via `POST /api/4.0/agents` without explicit user approval in Step 5. Apply LookML metadata changes strictly in `dev_mode`, verify `0` compilation errors via `validate_project` (auto-reverting on any error), and never auto-commit to production.

---

## Five-Step `build_agent` Execution Workflow

### Step 1: Validate Inputs *(Human Gate #1)*
Collect and validate the required configuration parameters before inspecting the instance (see [standalone_vs_dashboard_agents.md](references/standalone_vs_dashboard_agents.md)):
- **Agent Goal / Intent** *(Required)*: Target persona, business domain, and primary questions the agent must answer.
- **Agent Type** *(Required)*: `Standalone Agent` or `Dashboard Agent`.
- **Context & Business Rules** *(Optional)*: Fiscal calendar conventions, mandatory exclusions, metric disambiguation rules, and default time windows.
- **Target Explores** *(Optional for Standalone Agent)*: Specific `model.explore` targets. If omitted, discover candidate Explores automatically in Step 2.
- **Reference Dashboard URL / ID / Slug** *(Required for Dashboard Agent)*: The target dashboard backing the agent.

### Step 2: Inspect LookML & Determine Eval Dataset
1. **Inspect Semantic Metadata via Looker MCP:**
   - For **Standalone Agents**, run `get_explores` (discovering relevant Explores if none were provided), followed by `get_dimensions` and `get_measures` on selected Explores to catalog field names, `label`, `description`, `hidden` flags, `joins`, and `raw/` vs. `refined/` `+view_name` files.
   - For **Dashboard Agents**, run `get_dashboards` (and `run_dashboard` if needed) to extract tile titles, underlying `model.explore` targets, default dashboard filters, and KPI definitions, then inspect the backing Explores with `get_dimensions` and `get_measures`.
   - Sample ambiguous categorical filter fields with `get_field_value_suggestions` so exact database values can be inlined into the system instructions.
2. **Establish Baseline Eval Dataset (`3-5` Test Questions):**
   - Formulate **3 to 5 representative natural-language test questions** paired with verified Ground Truth `looker_query` payloads (tested via the Looker MCP `query` tool) covering core KPIs, time-series breakdowns, and categorical filters.

### Step 3: Develop Agent Configurations (`Plan A` & `Plan B`)
Author the complete agent package adhering to [looker-ca-best-practices.md](references/looker-ca-best-practices.md) and [lookml-ca-modeling-standards.md](references/lookml-ca-modeling-standards.md):
1. **Plan A — CA Agent Package (`A1..A3` — Target: Looker API 4.0 `POST /api/4.0/agents`):**
   - **`A1` (Four-Part XML/YAML System Instructions):** Draft concise instructions following [system_instructions_template.md](references/system_instructions_template.md) with explicit `<role_and_tone>`, `<explore_and_filtering_rules>`, `<semantic_and_execution_rules>`, and `<presentation_and_analysis_rules>` blocks. Inline verified filter values and enforce single-query consolidation.
   - **`A2` (Agent Metadata & Settings):** Define `name`, `description`, grounding targets (`explores` or `dashboard_id`), and advanced analytics settings (`code_interpreter`, chart generation).
   - **`A3` (Seed Golden Queries — `Standalone Agent` Only):** Create **3 to 5 seed Golden Queries** (strictly `< 20` total) following [golden_queries_and_deployment.md](references/golden_queries_and_deployment.md) with `<= 50%` exact match against the Step 2 baseline eval dataset.
2. **Plan B — Safe LookML Metadata Enrichments (`B1..Bn` — Target: Looker `dev_mode`):** Prepare surgical, non-destructive LookML additions (`description:`, `label:`, `primary_key: yes`) for any gaps discovered in Step 2, including a **`[LookML Safety & Impact Check]`** confirming that `+view_name` refinements and existing dashboards are preserved.

### Step 4: Run Pre-Presentation Quality Checks
Before presenting the configuration to the user, run automated quality checks:
1. **Zero Schema Errors:** Verify via Looker MCP `query` that every `model`, `explore`, `view.field`, filter, and sort in the seed Golden Queries and Baseline Eval Dataset executes with zero errors.
2. **System Instructions Budget & Structure Check:** Confirm all four XML/YAML sections are present, token length is within budget, no field catalogs are duplicated, and golden query exact-match overlap with the eval dataset is `<= 50%`.
3. **LookML Safety Verification:** Verify that every proposed LookML edit in `Plan B` targets the proper file (e.g., `views/refined/` when refinements are used) and will not break existing Explores or dashboards.

### Step 5: Interactive Plan Review & Authorized Subagent Deployment *(Human Gate #2)*
Present **Plan A (CA Agent Deployment)** and **Plan B (LookML `dev_mode` Enrichments)** clearly and request explicit user authorization before executing (see [golden_queries_and_deployment.md](references/golden_queries_and_deployment.md)):
1. **Present Full Visual Package (`Plan A` & `Plan B`):** Output `A1` (4-part system instructions), `A2` (agent metadata/settings), `A3` (seed Golden Queries JSON + 3-5 Baseline Eval pairs), and `B1..Bn` (LookML diffs with `[LookML Safety & Impact Check]`).
2. **Present Interactive Execution Menu (With Optional Parallel Subagents):** Allow the user to choose:
   - **Option 1 — Execute Plan A Only (`CA Agent Creator Subagent`):** Deploy the new CA Agent (`POST /api/4.0/agents`) and register seed golden queries (`POST /api/4.0/agents/{id}/golden_queries`) in Looker without modifying LookML.
   - **Option 2 — Execute Plan B Only in `dev_mode` (`LookML Dev-Branch Subagent`):** Switch to Looker `dev_mode`, apply `B1..Bn` via `update_project_file`, run `validate_project` to confirm `0` errors (auto-reverting on any error), and export `./ca_lookml_patch_<agent_id>.diff`.
   - **Option 3 — Execute Plan A & Plan B in Parallel (Launch Both Authorized Subagents):** Spawn both subagents concurrently to deploy the CA Agent in Looker API 4.0 and apply/validate LookML enrichments in `dev_mode`.
   - **Option 4 — Customize Subset or Export Printed Config Only:** Modify specific items (`A1..A3`, `B1..Bn`) or keep the printed configuration only without calling write endpoints.
