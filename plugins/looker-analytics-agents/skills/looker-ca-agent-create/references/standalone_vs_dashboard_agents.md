# Standalone Agents vs. Dashboard Agents: Architecture & Input Validation

This reference defines the architectural differences, input validation rules (Step 1), and Looker MCP discovery workflows (Step 2) for building Looker Conversational Analytics (CA) **Standalone Agents** and **Dashboard Agents**.

---

## 1. Architectural Comparison

| Attribute | Standalone Agent | Dashboard Agent |
| :--- | :--- | :--- |
| **Grounding Scope** | 1 to 5 curated LookML Explores (`model.explore`) | A single Looker Dashboard (`dashboard_id` or `slug`) and its underlying tile Explores |
| **Target Persona** | Domain analysts, business ops, and cross-functional teams asking open-ended questions | Executives, account managers, and stakeholders exploring a curated dashboard |
| **System Instructions Focus** | Cross-Explore routing, semantic metric disambiguation, default date/status filters, and cohort rules | Dashboard tile mapping, executive KPI definitions, filter inheritance rules, and drill-down guidance |
| **Golden Queries (`looker_golden_queries`)** | **Required (`3-5` seed queries, `< 20` cap)** to teach multi-view joins and complex filter archetypes | **Not applicable** (Dashboard tiles natively act as grounded query exemplars) |
| **LookML Metadata Dependency** | High across all exposed dimensions and measures in attached Explores | High on fields referenced by dashboard tiles, filters, and common drill paths |

---

## 2. Step 1 Input Validation Checklist

Before querying Looker MCP, validate the user's request against the five input parameters:

1. **Agent Goal / Intent *(Required)*:**
   - Must specify the business domain, target user persona, and primary analytical questions (for example: *"Help regional sales directors analyze pipeline velocity, win rates, and ARR churn"*).
   - If missing or vague, prompt the user to clarify the business objective.

2. **Agent Type *(Required)*:**
   - **`Standalone Agent`:** Choose when users need flexible ad-hoc querying across one or more LookML Explores independent of a specific dashboard layout.
   - **`Dashboard Agent`:** Choose when the conversational experience is anchored to an existing Looker Dashboard and its KPI tiles.

3. **Context & Business Rules *(Optional)*:**
   - Capture domain-specific rules: fiscal year start month, standard exclusions (such as `is_test_account = no` or `order_status != 'Cancelled'`), currency conventions, and default time windows (such as `last 30 complete days`).
   - If omitted, infer baseline conventions from LookML field descriptions and dashboard filters during Step 2 and highlight them for confirmation in Step 5.

4. **Target Explores *(Optional for Standalone Agent)*:**
   - Accept 1 to 5 `model_name.explore_name` targets.
   - **Auto-Discovery Fallback:** If the user selects `Standalone Agent` without naming Explores, automatically run `get_models` and `get_explores` in Step 2 to rank and select the most relevant curated Explores matching the Agent Goal.
   - **Mega-Explore Warning:** If an Explore exposes more than 15 joined views or hundreds of uncurated fields, recommend scoping a narrower Explore or hiding unused fields via LookML `fields:` / `hidden: yes`.

5. **Reference Dashboard URL / ID / Slug *(Required for Dashboard Agent)*:**
   - Must resolve to a valid Looker Dashboard via `get_dashboards` or `get_dashboard`.
   - If the user requests a `Dashboard Agent` without providing a dashboard identifier, halt at Step 1 and ask for the Dashboard URL, ID, or slug.

---

## 3. Step 2 LookML & Dashboard Inspection Workflow

### Flow A: Standalone Agent Discovery
1. Call `get_explores` for the target model(s) to verify Explore existence, labels, and descriptions.
2. Call `get_dimensions` and `get_measures` for each target Explore.
3. Audit exposed fields against `lookml-ca-modeling-standards.md`:
   - Flag measures or dimensions used by core KPIs that lack `description:` or human-readable `label:`.
   - Flag exposed primary/foreign keys (`_id`, `_pk`, `_sk`) missing `hidden: yes`.
   - Inspect `.model.lkml` / `.view.lkml` via `get_project_file` to verify every joined view declares `primary_key: yes`.
4. Call `get_field_value_suggestions` on key status, category, or region dimensions to capture exact canonical strings for the `<explore_and_filtering_rules>` block.

### Flow B: Dashboard Agent Discovery
1. Call `get_dashboards` / `get_dashboard` using the provided Dashboard ID or slug.
2. Extract:
   - Dashboard title, description, and global dashboard filters (`default_value`, `field`).
   - Every query tile's title, `model`, `explore`, `fields`, `filters`, and `sorts`.
3. Call `get_dimensions` and `get_measures` on each backing `model.explore` used by the dashboard tiles to identify natural drill-down dimensions and verify metadata completeness.

---

## 4. Formulating the Baseline Eval Dataset (`3-5` Questions)

In Step 2, construct **3 to 5 representative evaluation questions** paired with verified Ground Truth `looker_query` definitions:

| Question Archetype | Purpose | Ground Truth Verification |
| :--- | :--- | :--- |
| **1. Headline KPI + Default Filter** | Verifies default time window and mandatory exclusion rules | Run via Looker MCP `query` tool and confirm non-empty results |
| **2. Dimensional Breakdown / Top-N** | Verifies grouping dimension selection and sorting rules | Confirm `fields`, `sorts`, and `limit` match business expectations |
| **3. Disambiguated Metric / Ratio** | Tests selection between closely named measures (e.g., Gross vs. Net) | Confirm exact measure name from `get_measures` |
| **4. Categorical Value Mapping** | Tests inlined filter synonyms (e.g., `"Enterprise"` -> `"ENT_TIER_1"`) | Verify filter string via `get_field_value_suggestions` |
| **5. Multi-View Join or Cohort Filter** | Tests cross-view join integrity and symmetric aggregation | Verify zero fanout errors and valid SQL generation |
