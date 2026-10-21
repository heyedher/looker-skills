---
name: looker-ca-agent-optimize
description: >-
  Audits and optimizes Looker Conversational Analytics (CA) Standalone and
  Dashboard Agents for accuracy and latency. Use when the user asks to audit a
  Looker CA agent against best practices, diagnose thought loops, field-sampling
  loops, or data-hunting loops in CA reasoning traces, optimize CA system
  instructions and golden queries, or run Side-by-Side (SxS) agent evaluations.
  Do not use for creating a brand-new CA agent from scratch (use
  looker-ca-agent-create) or optimizing general LookML SQL/PDT queries (use
  lookml-performance-optimizer).
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

# Looker Conversational Analytics (CA) Agent Performance Optimizer

## Overview

This skill audits and optimizes existing Looker Conversational Analytics (CA) Standalone Agents and Dashboard Agents to improve **Accuracy** (matching ground-truth query results) and reduce **Latency** (P50/P90 response time).

**Prerequisite:** If the Looker MCP tools or Looker CLI are unavailable, ask the user to install `looker-base` first.

---

## Operating Modes

Because running live evaluations consumes Conversational Analytics tokens, this skill supports two explicit modes:

| Mode | Basis | Live CA Eval Runs / Token Usage? | Execution Path |
| :--- | :--- | :--- | :--- |
| **`Audit`** *(Default)* | Static adherence check of instructions, settings, golden queries, and LookML against best practices. | **None** (`0` CA runs) | Steps 1 -> 2 -> 3 -> 6 -> 7 |
| **`Optimize`** | Live CA Agent reasoning-trace analysis + up to 2 rounds of Side-by-Side (SxS) validation. | **Yes** (Baseline + up to 2 SxS rounds) | Steps 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 |

---

## Behavioral Guardrails (Mandatory)

1. **Three Human-in-the-Loop Gates Only:** Request user input strictly at **Step 1** (Inputs), **Step 6** (Interactive Review of **Plan A: CA Agent** and **Plan B: LookML `dev_mode`**), and **Step 7** (Authorized Execution via Direct Tools or Parallel Subagents). Execute Steps 2 through 5 automatically.
2. **Reality Mapping & LookML Refinement Awareness:** Never invent Explore names, field names, or agent settings. When inspecting LookML files via `get_project_file`, distinguish **LookML Refinements (`view: +view_name` across `raw/` and `refined/` layers)** from duplicate fields—refinements merge into a single field and must never be flagged as duplicates. Never propose destructive LookML changes (`hidden: yes`) without verifying they will not break existing Explores, joins, or dashboards.
3. **Surgical Modification & Rollback Safety:** Never overwrite an existing agent in place during SxS testing (use a temporary `[TMP-SXS-EVAL]` agent copy and delete it afterward). Always snapshot the previous agent configuration before applying approved updates, validate LookML edits in `dev_mode` via `validate_project` (auto-reverting on any error), and never auto-commit LookML changes to production.

---

## Seven-Step Execution Workflow

### Step 1: Collect & Validate User Inputs *(Human Gate #1)*
Prompt the user for any missing required inputs before proceeding:
- **Looker Instance URL / Connection** *(Required)*
- **CA Agent Identifier** *(Required)*: Agent ID, Agent URL, or raw Agent configuration JSON (infer whether Standalone or Dashboard Agent).
- **Mode** *(Optional, default: `Audit`)*: `Audit` or `Optimize`.
- **Target Metric** *(Optional, `Optimize` mode only, default: `All`)*: `Accuracy`, `Latency`, or `All`.
- **Eval Suite** *(Required for `Optimize`, optional for `Audit`)*: Text, CSV, or Sheet containing `(User Question, Ground Truth Query/Tile, Issue Description)`.

### Step 2: Automatic Looker & Agent Connection Setup
1. Load the CA Agent configuration (`instructions`, attached Explores/Dashboard, `golden_queries`, advanced settings) and inspect LookML metadata (`label`, `description`, `hidden`, `joins`, `primary_key`, and `raw/` vs. `refined/` `+view_name` structure) using the endpoints in [ca_api_and_mcp_workflow.md](references/ca_api_and_mcp_workflow.md).
2. If access is blocked (`403` / missing permissions), stop and report the exact missing Looker role or GCP IAM permission.
3. Output a concise one-line setup summary (for example: `"Connected: Standalone Agent with 2 Explores and 6 golden queries."`).

### Step 3: Static Best-Practice Audit *(Both Modes)*
Evaluate the loaded agent and LookML against [looker-ca-best-practices.md](references/looker-ca-best-practices.md) and [lookml-ca-modeling-standards.md](references/lookml-ca-modeling-standards.md):
- **Instructions:** Check 4-part XML/YAML structure, token budget, field name validity against live LookML, and conflicting/hardcoded rules.
- **Explore Scoping & Golden Queries:** Check for noisy mega-explores, golden query count (`< 20`), duplicates, or overfitting (`> 50%` exact match).
- **LookML Metadata (With Refinement & Safety Check):** Identify exposed fields missing `description:`/`label:`, unhidden internal keys, or joined views missing `primary_key: yes`. Verify that repeated definitions across `.view.lkml` files are not LookML Refinements (`view: +view_name`) before flagging redundancy. If a field is ambiguous only for the CA Agent, prefer disambiguating it in the CA Agent instructions (`Plan A`) over hiding fields in LookML (`Plan B`).
- **Routing Rule:** If `Mode == Audit`:
  - If zero gaps are found, output: `"No best-practice gaps found. Run Optimize mode to analyze live CA agent behavior."` and stop.
  - Otherwise, mark all findings as `"Not validated in SxS"` and jump directly to **Step 6**.

### Step 4: Baseline Run & Reasoning-Trace Diagnosis *(`Optimize` Mode Only)*
1. Execute the Eval Suite against the current CA Agent and record baseline **Accuracy** (e.g., `6 of 10`) and directional **P50 / P90 Latency**.
2. Inspect the reasoning traces (`thoughts` and tool calls) using [reasoning_trace_diagnostics.md](references/reasoning_trace_diagnostics.md) to classify failures into:
   - **Thought Loops / Multi-Query Stacking**
   - **Field-Sampling Loops** (repeated `get_field_value_suggestions` calls)
   - **Data-Hunting Loops** (guessed date filters returning `0` rows)
   - **Semantic & Filter Ambiguity**
3. Merge trace-level root causes with the static findings from Step 3.

### Step 5: Cheapest-First Drafting & 2-Round SxS Self-Check *(`Optimize` Mode Only)*
Follow the iterative SxS protocol in [sxs_evaluation_workflow.md](references/sxs_evaluation_workflow.md):
1. Draft fixes ordered cheapest-first: **(1) Prune/simplify instructions -> (2) Metadata settings -> (3) Targeted instruction rules -> (4) Golden queries (`< 20`) -> (5) Safe LookML metadata**.
2. Run **Round 1 SxS** on a temporary draft copy of the agent (`[TMP-SXS-EVAL]`). If the target metric improves with zero regressions, proceed to **Step 6**.
3. Otherwise, refine using Round 1 traces and run **Round 2 SxS (Final)**. Delete the temporary agent copy (`DELETE /api/4.0/agents/{temp_id}`) immediately after evaluation.

### Step 6: Present Scorecard & Two Interactive Execution Plans *(Human Gate #2)*
Present the structured report defined in [sxs_evaluation_workflow.md](references/sxs_evaluation_workflow.md), explicitly separating CA Agent changes from LookML changes:
1. **Verdict & SxS Scorecard (`Optimize` only):** `Improved` / `Partial` / `No further optimization` / `Audit only`, plus Baseline vs. Proposed Accuracy and P50/P90 Latency (highlighting any metric trade-offs).
2. **Plan A — CA Agent Configuration Plan (`A1..An` — Target: Looker API 4.0 `PATCH /api/4.0/agents/{id}`):** Table and full `Before -> After` visual diffs for System Instructions, Agent Settings, and Golden Queries.
3. **Plan B — Validated LookML Dev-Branch Plan (`B1..Bn` — Target: Looker `dev_mode` via MCP `update_project_file` + `validate_project`):** Table and `Before -> After` diffs for safe LookML metadata edits (`description:`, `label:`, `primary_key: yes`), each including an explicit **`[LookML Safety & Impact Check]`** confirming it respects `+view_name` refinements and will not break existing Explores/Dashboards.
4. **Interactive Authorization Menu (With Optional Parallel Subagents):** Present the 5 clear execution options from [sxs_evaluation_workflow.md](references/sxs_evaluation_workflow.md) so the user can choose to run **Plan A only (Subagent 1)**, **Plan B in `dev_mode` only (Subagent 2)**, **Both Plan A & Plan B in parallel (2 Subagents)**, **Run SxS on a temporary `[TMP-SXS-EVAL]` agent first**, or **Customize/Discard specific items (`A1..An`, `B1..Bn`)**.

### Step 7: Execute Authorized Plan(s) & Rollback Safety *(Human Gate #3 — PRD Step 8)*
Only after explicit user selection in Step 6, execute the authorized plan(s) (directly or by spawning the authorized subagent(s)) following [ca_api_and_mcp_workflow.md](references/ca_api_and_mcp_workflow.md):
1. **If Plan A (`CA Agent Updater`) is authorized:** Save a local JSON rollback snapshot (`./ca_agent_backup_<agent_id>_<timestamp>.json`), then apply approved `A1..An` instruction, setting, and golden-query updates via `PATCH /api/4.0/agents/{id}` (and `/golden_queries`).
2. **If Plan B (`LookML Dev-Branch Updater`) is authorized:** Switch to `dev_mode` (`enable: true`), apply approved `B1..Bn` edits to the appropriate `.view.lkml` file (targeting `refined/` views when refinements are used) via `update_project_file`, run `validate_project` (and `run_lookml_tests`) to confirm `0` errors (reverting immediately if any error is introduced), export `./ca_lookml_patch_<agent_id>.diff` + handoff note, and never auto-commit to production.
