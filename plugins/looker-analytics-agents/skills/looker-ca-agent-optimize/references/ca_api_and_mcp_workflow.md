# Looker API 4.0 CA Endpoints & Looker MCP Integration Workflow

Because Looker MCP does not yet provide dedicated tools for Looker API 4.0 `ConversationalAnalytics` endpoints, `looker-ca-agent-optimize` uses a **hybrid execution contract**:
- **Looker MCP Tools (`looker-base`):** Used for all LookML inspection, field sampling verification, ground-truth query execution, and development-branch LookML patching.
- **Looker API 4.0 REST / CLI (`ConversationalAnalytics`):** Used to load CA Agent configurations, execute evaluation conversations, manage temporary SxS agents, and apply approved agent updates.

---

## 1. Looker MCP Tool Mapping (Steps 2, 3, 4, 5, and 8)

Use the following Looker MCP tools provided by `looker-base`:

| Workflow Step | Looker MCP Tool | Purpose |
| :--- | :--- | :--- |
| **Steps 2 & 3 (LookML Metadata Audit)** | `get_explores`, `get_dimensions`, `get_measures`, `get_project_file`, `health_analyze` | Inspect field `label`, `description`, `hidden` flags, Explore `joins`, and `primary_key` declarations for all Explores attached to the CA Agent. |
| **Steps 4 & 5 (Ground Truth & Sampling Diagnosis)** | `query`, `get_field_value_suggestions` | Execute Ground Truth Looker queries to verify expected data results and inspect categorical field values when diagnosing Field-Sampling Loops or Data-Hunting Loops. |
| **Step 8 (LookML Dev-Branch Patch)** | `dev_mode`, `update_project_file`, `validate_project`, `run_lookml_tests` | Switch to the developer branch (`dev_mode`), apply surgical LookML metadata improvements (`update_project_file`), and verify zero compilation errors (`validate_project`). Never deploy to production. |

---

## 2. Looker API 4.0 `ConversationalAnalytics` Endpoints

Invoke the Looker 4.0 REST endpoints (`/api/4.0/...`) via `looker-cli` or authenticated REST requests against `<looker_instance_url>`:

### A. Load CA Agent Configuration (Step 2)
- **Endpoint:** `GET /api/4.0/agents/{agent_id}`
- **Response Fields Used:**
  - `id`, `name`, `description`
  - `system_instruction` / `context` (current instructions and settings)
  - `explores` / `dashboard_id` (infer Standalone Agent vs. Dashboard Agent)
  - `golden_queries` / `looker_golden_queries`

### B. Execute Eval Suite Questions & Capture Reasoning Traces (Steps 4 & 5)
1. **Create Evaluation Conversation:**
   - **Endpoint:** `POST /api/4.0/conversations`
   - **Payload:** `{"agent_id": "<agent_id_or_temp_sxs_id>"}`
2. **Send Test Question & Capture Trace + Timing:**
   - **Endpoint:** `POST /api/4.0/conversational_analytics/chat`
   - **Payload:** `{"conversation_id": "<conv_id>", "message": "<eval_question>"}`
   - **Captured Telemetry:**
     - Wall-clock response duration (used to compute directional P50 and P90 latency across the Eval Suite).
     - Reasoning steps / `thoughts` and intermediate Looker queries (used to detect Thought Loops, Field-Sampling Loops, and Data-Hunting Loops).
     - Final generated `looker_query` and data payload (compared against the Eval Suite Ground Truth).

### C. Temporary SxS Agent Creation & Cleanup (Step 5)
- **Create Temporary SxS Copy:** `POST /api/4.0/agents` (using the draft `system_instruction` and `golden_queries` payload with name prefixed by `[TMP-SXS-EVAL]`).
- **Delete Temporary SxS Copy:** `DELETE /api/4.0/agents/{temp_agent_id}` (mandatory immediately after SxS evaluation completes).

### D. Apply Approved CA Agent Updates & Rollback Snapshot (Step 8)
Execute **only after explicit human approval in Step 6**:
1. **Save Rollback Snapshot:** Write the original `GET /api/4.0/agents/{agent_id}` JSON payload to `./ca_agent_backup_<agent_id>_<timestamp>.json` and report the file path to the user.
2. **Update Agent Configuration:**
   - **Endpoint:** `PATCH /api/4.0/agents/{agent_id}`
   - **Payload:** Updated `system_instruction` and metadata settings approved by the user.
3. **Sync Golden Queries (Standalone Agents):**
   - **Endpoints:** `POST /api/4.0/agents/{agent_id}/golden_queries`, `PATCH /api/4.0/agents/{agent_id}/golden_queries/{gq_id}`, or `DELETE /api/4.0/agents/{agent_id}/golden_queries/{gq_id}`.
4. **Export LookML Patch & Handoff Note:**
   - Save the unified diff of modified `.view.lkml` / `.model.lkml` files to `./ca_lookml_patch_<agent_id>.diff` along with a summary of `What changed`, `Why`, and `Affected Eval Questions`.
