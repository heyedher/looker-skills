# Side-by-Side (SxS) Evaluation & Scorecard Workflow

This reference governs **Step 5 (Drafting & 2-Round SxS Self-Check)** and **Step 6 (Recommendations & SxS Scorecard)** of `looker-ca-agent-optimize`.

---

## 1. Cheapest-First Drafting Hierarchy (Step 5)

When synthesizing candidate improvements from Step 3 (Static Audit) and Step 4 (Trace Diagnosis), always prioritize modifications from lowest token/maintenance cost to highest:

1. **Priority 1 — Prune & Simplify System Instructions:**
   - Remove redundant prose, duplicated field lists, or conflicting rules that inflate prompt tokens.
   - Restructure plain-text instructions into the 4-part XML/YAML template (`<role_and_tone>`, `<explore_and_filtering_rules>`, `<semantic_and_execution_rules>`, `<presentation_and_analysis_rules>`).
2. **Priority 2 — Agent Metadata & Explore Scoping Settings:**
   - Remove unnecessary attached Explores if the agent's scope only requires a subset.
3. **Priority 3 — Targeted System Instruction Additions:**
   - Add single-query consolidation rules (fixing Thought Loops), inlined categorical value mappings (fixing Field-Sampling Loops), and conditional date-filter exceptions (fixing Data-Hunting Loops).
4. **Priority 4 — Golden Queries (`looker_golden_queries` — Standalone Agents Only):**
   - Deduplicate or prune low-value golden queries to keep the total count strictly `< 20`.
   - Add 1–3 targeted golden queries for complex join or cohort patterns that failed in Step 4 (never exceeding 50% exact match with the Eval Suite).
5. **Priority 5 — LookML Semantic Layer Metadata:**
   - Propose `description:`, `label:`, `hidden: yes`, and `primary_key: yes` patches on the underlying `.view.lkml` and `.model.lkml` files.

---

## 2. Two-Round SxS Evaluation Protocol (Temporary Agent Copy)

Because Looker API 4.0 does not expose a stateless draft-preview chat endpoint for modified agent configs, execute SxS validation safely without mutating the production agent:

1. **Create Temporary Draft Agent Copy:**
   - Clone the baseline agent configuration JSON with a temporary name (`"[TMP-SXS-EVAL] <Original Agent Name>"`) via `POST /agents` (or test LookML changes on the developer branch).
2. **Round 1 SxS Execution:**
   - Run all questions from the Eval Suite against the temporary agent copy (`POST /conversations` + `POST /conversational_analytics/chat`).
   - Compare **Round 1 Accuracy** and **Directional P50 / P90 Latency** against the Step 4 Baseline:
     - **Pass Criteria:** Target metric improves (e.g., Accuracy increases from `6/10` to `9/10` or P50/P90 Latency drops by `> 20%`) with **zero regressions** on previously passing questions -> Proceed to **Step 6**.
     - **Needs Refinement:** If any regression occurs or target questions still fail, inspect Round 1 reasoning traces and proceed to **Round 2**.
3. **Round 2 SxS Execution (Final Cap):**
   - Adjust the draft instructions/golden queries based on Round 1 traces and re-run the Eval Suite.
   - If Round 2 improves the target metric, proceed to **Step 6**.
   - If no net improvement is achieved after 2 rounds, select the better-performing round, document the remaining failing questions and root cause (e.g., missing underlying data or LookML join limitation), and exit to **Step 6**.
4. **Mandatory Cleanup:**
   - Always delete the temporary draft agent (`DELETE /agents/{temp_id}`) immediately after Round 1 / Round 2 completes so no orphaned copy remains in the Looker instance.

---

## 3. Step 6 Output Format: SxS Scorecard & Two Interactive Execution Plans

Present the optimization results to the user using the exact structure below before requesting approval. Always separate **Plan A (CA Agent Changes)** from **Plan B (Validated LookML Dev-Branch Changes)** so the user knows exactly where each change will be applied:

### A. Verdict & Summary
- **Verdict:** `Improved` | `Partial Improvement` | `No Further Optimization Possible (state reason & owner)` | `Audit Only`
- **Metric Trade-off Alert (if applicable):** If Accuracy improved but P50/P90 Latency increased (or vice versa), highlight the trade-off explicitly so the user can decide.

### B. SxS Performance Scorecard (`Optimize` Mode Only)

| Metric | Baseline (Current Agent) | Proposed (Best SxS Round) | Measured Delta / Lift |
| :--- | :--- | :--- | :--- |
| **Accuracy (Ground Truth Match)** | `X of N` (`XX%`) | `Y of N` (`YY%`) | `+Z` questions (`+ZZ%`) |
| **P50 Latency (Directional)** | `XX.Xs` | `YY.Ys` | `-ZZ%` |
| **P90 Latency (Directional)** | `XX.Xs` | `YY.Ys` | `-ZZ%` |
| **Reasoning Loop Failures** | `M` questions with loops | `K` questions with loops | `-L` loops eliminated |

### C. Plan A — CA Agent Configuration Plan (Target: Looker API 4.0 `PATCH /api/4.0/agents/{id}`)
*Where it applies:* Updates the CA Agent directly in the Looker instance via API 4.0 after saving a local rollback snapshot (`./ca_agent_backup_<agent_id>_<timestamp>.json`). Does not touch any LookML files.

| ID | Change Summary | Component (`Instructions` / `Settings` / `Golden Queries`) | Expected Impact | Measured in SxS (`Validated` / `Not validated`) |
| :--- | :--- | :--- | :--- | :--- |
| `A1` | Restructure `context.instructions` into 4-part XML, fix field names, and inline categorical filter values | `Instructions` | Eliminates field-sampling loops and invalid field errors (`-35%` latency) | `Validated` / `Not validated` |
| `A2` | Enable `code_interpreter: true` in agent settings | `Settings` | Enables derived rate and statistical calculations | `Validated` / `Not validated` |
| `A3` | Register verified Golden Queries (`< 20` cap, `<= 50%` overlap) | `Golden Queries` | Fixes multi-view join path selection | `Validated` / `Not validated` |

For each item (`A1..An`), display:
- **What (`Before -> After`):** Complete, inspectable diff of the instruction block, setting, or golden query JSON.
- **Why & Expected Effect:** Root cause or trace evidence and affected questions.

### D. Plan B — Validated LookML Dev-Branch Plan (Target: Looker `dev_mode` via MCP `update_project_file` + `validate_project`)
*Where it applies:* Switches to the user's isolated Looker development branch (`dev_mode`), applies surgical metadata edits to `.view.lkml` files (targeting `views/refined/` when `+view_name` refinements are used), runs `validate_project` to confirm `0` compilation errors (auto-reverting if any error occurs), and exports `./ca_lookml_patch_<agent_id>.diff`. Never auto-commits to production.

| ID | Target LookML File & View | Change Summary | `[LookML Safety & Impact Check]` | Measured in SxS |
| :--- | :--- | :--- | :--- | :--- |
| `B1` | `views/refined/session_facts.view.lkml` (`+session_facts`) | Add missing `description:` to `session_start` and `session_end` | **Safe (Additive metadata only):** Respects `+session_facts` refinement layer; zero impact on existing queries or dashboards. | `Not validated` *(Dev branch)* |

For each item (`B1..Bn`), display:
- **What (`Before -> After`):** Exact LookML snippet diff and target file path.
- **`[LookML Safety & Impact Check]`:** Verification that the edit does not misinterpret LookML refinements (`view: +view_name`) as duplicates and will not break existing Explores, joins, or dashboards.

### E. Interactive Authorization Menu (With Optional Parallel Subagents)
Always conclude Step 6 by presenting these 5 interactive choices to the user:

1. **Option 1 — Execute Plan A Only (`CA Agent Updater Subagent`):** Save local rollback JSON (`./ca_agent_backup_<agent_id>_<timestamp>.json`) and apply `A1..An` directly to the CA Agent in Looker via API 4.0, leaving LookML untouched.
2. **Option 2 — Execute Plan B Only in `dev_mode` (`LookML Dev-Branch Subagent`):** Switch to Looker `dev_mode`, apply `B1..Bn` via `update_project_file`, run `validate_project` / `run_lookml_tests` to confirm `0` LookML errors (auto-reverting on any error), and export `./ca_lookml_patch_<agent_id>.diff`.
3. **Option 3 — Execute Plan A & Plan B in Parallel (Launch Both Authorized Subagents):** Spawn **Subagent 1 (`CA Agent Updater`)** and **Subagent 2 (`LookML Dev-Branch Updater`)** concurrently to apply Plan A in Looker API 4.0 and Plan B in Looker `dev_mode`.
4. **Option 4 — Test Plan A First on a Temporary `[TMP-SXS-EVAL]` Agent (`Optimize` Mode SxS):** Create a temporary clone of the agent, run 3-5 test questions Side-by-Side to measure live Accuracy/Latency lift, delete the temporary agent, and return the scorecard before touching the real agent.
5. **Option 5 — Customize Subset or Keep Printed Output Only:** Specify exact items to apply or discard (e.g., *"Apply A1, A2, A3 and B1, discard B2"*) or ask questions about any proposed change.
