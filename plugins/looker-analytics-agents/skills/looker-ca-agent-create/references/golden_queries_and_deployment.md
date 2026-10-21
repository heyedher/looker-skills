# Golden Queries Curation, Quality Validation & API 4.0 Deployment

This reference covers seed Golden Query curation (Step 3), pre-deployment validation checks (Step 4), and Looker API 4.0 deployment endpoints (Step 5) for `looker-ca-agent-create`.

---

## 1. Seed Golden Query Standards (`Standalone Agent` Only)

Golden Queries (`looker_golden_queries`) provide few-shot exemplars that teach a Standalone Agent how to construct accurate Looker queries across complex joins, date windows, and business cohorts.

### Curation Guardrails
1. **Seed Quantity (`3 to 5` Initial, `< 20` Hard Cap):**
   - Author **3 to 5 high-signal seed Golden Queries** when creating a new Standalone Agent. Never exceed 19 total golden queries (`< 20`), as excess exemplars inflate prompt latency.
2. **Anti-Overfitting Rule (`<= 50%` Overlap with Eval Dataset):**
   - Seed golden queries must represent generalizable **query archetypes** (e.g., multi-view join, period-over-period trend, filtered cohort ranking) rather than verbatim copies of the evaluation test suite.
   - At most **50%** of the Step 2 Baseline Eval Dataset questions may have an exact structural match in `looker_golden_queries` (for example, at most 2 golden queries for a 4-question eval set, or teach adjacent dimensions/timeframes).
3. **Mandatory Verification via Looker MCP `query`:**
   - Every seed golden query must be executed via the Looker MCP `query` tool in Step 4 to confirm that `model`, `explore`, `fields`, `filters`, and `sorts` compile and return valid rows.

### Golden Query JSON Schema
```json
[
  {
    "natural_language_questions": [
      "What was our net revenue by product category last month?",
      "Break down monthly net sales by category for the previous calendar month"
    ],
    "looker_query": {
      "model": "retail_analytics",
      "explore": "order_items",
      "fields": [
        "products.category",
        "order_items.net_revenue",
        "order_items.order_count"
      ],
      "filters": [
        {"field": "order_items.created_date", "value": "last 1 month"},
        {"field": "order_items.status", "value": "Complete"}
      ],
      "sorts": ["order_items.net_revenue desc"],
      "limit": "10"
    }
  }
]
```

---

## 2. Step 4 Quality & Baseline Validation Checklist

Before presenting the agent package to the user in Step 5, verify that all four quality checks pass:

| Check | Verification Method | Pass Criteria |
| :--- | :--- | :--- |
| **1. Schema & Query Validity** | Run every Golden Query and Baseline Eval ground-truth query via Looker MCP `query` | `0` invalid field, explore, filter, or SQL errors |
| **2. Instruction Structure & Budget** | Inspect generated `system_instruction` | All 4 XML/YAML sections present; `< 1,200` tokens; zero raw field dumps |
| **3. Anti-Overfitting Compliance** | Compare `looker_golden_queries` against the 3-5 Baseline Eval questions | `< 20` golden queries total; `<= 50%` exact question/query overlap |
| **4. LookML Compilation (`dev_mode`)** | Run `dev_mode` (`enable: true`), `update_project_file`, and `validate_project` | `0` LookML errors introduced; changes stay on dev branch |

---

## 3. Step 5 Two-Plan Presentation Format (`Plan A` vs. `Plan B`)

Always present the complete agent specification to the user split into two explicit, interactive plans before invoking any write endpoints on Looker API 4.0 or Looker MCP:

1. **Plan A — New CA Agent Deployment Plan (`A1..A3` — Target: Looker API 4.0 `POST /api/4.0/agents`):**
   - **`A1` (4-Part System Instructions):** Full XML or YAML block (`<role_and_tone>`, `<explore_and_filtering_rules>`, `<semantic_and_execution_rules>`, `<presentation_and_analysis_rules>`).
   - **`A2` (Agent Metadata & Settings):** `name`, `description`, Agent Type (`Standalone` vs. `Dashboard`), Grounding Targets (`explores` or `dashboard_id`), and Advanced Settings (`code_interpreter`).
   - **`A3` (Seed Golden Queries & Baseline Eval Dataset):** 3-5 verified `looker_golden_queries` payloads (`Standalone` only) and 3-5 Baseline Eval Dataset pairs.
2. **Plan B — Validated LookML Dev-Branch Plan (`B1..Bn` — Target: Looker `dev_mode` via MCP `update_project_file` + `validate_project`):**
   - Unified diff of safe, non-destructive LookML metadata enrichments (`description:`, `label:`, `primary_key: yes`) targeting the appropriate `.view.lkml` file (always targeting `views/refined/` when `+view_name` refinements are used).
   - Each item (`B1..Bn`) must include an explicit **`[LookML Safety & Impact Check]`** confirming that LookML refinements (`view: +view_name`) are respected and no existing Explores or dashboards are broken.
3. **Interactive Execution Menu (With Optional Parallel Subagents):**
   - **Option 1 — Execute Plan A Only (`CA Agent Creator Subagent`):** Deploy the new CA Agent and seed golden queries via Looker API 4.0, leaving LookML untouched.
   - **Option 2 — Execute Plan B Only in `dev_mode` (`LookML Dev-Branch Subagent`):** Switch to `dev_mode`, apply `B1..Bn` via `update_project_file`, run `validate_project` to confirm `0` errors (auto-reverting on any error), and export `./ca_lookml_patch_<agent_id>.diff`.
   - **Option 3 — Execute Plan A & Plan B in Parallel (Launch Both Authorized Subagents):** Spawn **Subagent 1 (`CA Agent Creator`)** and **Subagent 2 (`LookML Dev-Branch Updater`)** concurrently.
   - **Option 4 — Customize Subset or Export Printed Config Only:** Select specific items (`A1..A3`, `B1..Bn`) or keep the printed output without calling write endpoints.

---

## 4. Direct Deployment via Looker API 4.0 (Upon User Approval Only)

Once the user explicitly approves deployment in Step 5, invoke the Looker API 4.0 `ConversationalAnalytics` endpoints via `looker-cli` or authenticated REST calls:

### A. Create the CA Agent (`POST /api/4.0/agents`)
- **Endpoint:** `POST /api/4.0/agents`
- **Standalone Agent Payload:**
```json
{
  "name": "Retail Merchandising Analytics Agent",
  "description": "Answers revenue, margin, and inventory questions from curated retail Explores.",
  "explores": [
    {"model": "retail_analytics", "explore": "order_items"},
    {"model": "retail_analytics", "explore": "inventory_snapshot"}
  ],
  "system_instruction": "<agent_instructions>...</agent_instructions>",
  "settings": {
    "enable_chart_generation": true,
    "default_row_limit": 50
  }
}
```
- **Dashboard Agent Payload:** Replace `"explores"` with `"dashboard_id": "<dashboard_id>"` and omit golden queries.

### B. Register Seed Golden Queries (`POST /api/4.0/agents/{agent_id}/golden_queries`)
For Standalone Agents, iterate over the approved 3-5 seed golden queries and register each exemplar:
- **Endpoint:** `POST /api/4.0/agents/{agent_id}/golden_queries`
- **Payload:** Single golden query object (`natural_language_questions` and `looker_query`).

### C. Post-Deployment Smoke Test & Artifact Export
1. **Smoke Test Conversation (Optional):** Create a conversation via `POST /api/4.0/conversations` (`{"agent_id": "<agent_id>"}`) and run the 3-5 baseline eval questions via `POST /api/4.0/conversational_analytics/chat` to report live baseline accuracy and P50/P90 latency.
2. **Export Local Artifacts:**
   - Save the created agent JSON response (`agent_id`, URL, instructions, and golden query IDs) to `./ca_agent_created_<agent_id>.json`.
   - Save the validated LookML dev-branch diff to `./ca_lookml_patch_<agent_id>.diff` with handoff instructions for peer review. Never auto-commit LookML changes to production.
