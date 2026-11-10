---
name: looker-developer-onboarding
description: >-
  Orchestrate the end-to-end Looker developer onboarding workflow from system
  pre-flight checks and BigQuery data discovery to CLI setup, OAuth
  authentication, BigQuery connection creation, Looker project and Git setup,
  LookML model authoring, and interactive dashboard creation. Use when setting
  up a new Looker instance or onboarding a developer from scratch. Do not use
  for standalone LookML authoring on an already-onboarded project (use
  lookml-author).
license: Apache-2.0
compatibility: Requires looker-base (Looker MCP and looker-cli).
metadata:
  version: 1.0.0
  domain: looker-onboarding-migration
  role: orchestrator
  status: ga
  usage-interface: looker-cli
  publisher: google
  shared-refs: looker-cli-setup looker-cli-auth lookml-style-guide preflight_check
---

# Looker Developer Onboarding Orchestrator (`looker-developer-onboarding`)

This orchestrator skill guides a developer through the complete end-to-end Looker onboarding journey in strict sequence. Verify each step's success criteria before advancing to the next step.

> **Prerequisite:** If the Looker MCP tools or Looker CLI are unavailable, ask the user to install `looker-base` first.

---

## Step-by-Step Onboarding Sequence

| Step | Goal | Reference Guide | Success Verification |
| :--- | :--- | :--- | :--- |
| **1. Pre-flight Check** | Verify system (`gcloud`, `bq`, write permissions) prerequisites | [references/onboarding-preflight-check.md](references/onboarding-preflight-check.md) | `scripts/preflight_check.sh --mode system` exits `0` |
| **2. Data Discovery** | Interview user, explore BigQuery tables, and propose dashboard goal | [references/exploring-data-for-looker.md](references/exploring-data-for-looker.md) | User confirms proposed dashboard goal and target tables |
| **3. CLI Setup** | Verify `looker-cli` is in `PATH` or install from GitHub Releases | [references/looker-cli-setup.md](references/looker-cli-setup.md) | `looker-cli --help` executes cleanly |
| **4. CLI Authentication** | Configure profile, complete OAuth login, and check Looker roles | [references/looker-cli-auth.md](references/looker-cli-auth.md) | `looker-cli user me` returns user with `develop` permissions |
| **5. BigQuery Connection** | Verify Looker SA IAM roles and register ADC BigQuery connection | [references/connecting-looker-to-bigquery.md](references/connecting-looker-to-bigquery.md) | `looker-cli connection cat {name}` returns connection JSON |
| **6. Project & Git Setup** | Create Looker project in dev workspace and configure bare Git | [references/looker-project-setup.md](references/looker-project-setup.md) | `looker-cli project cat {id}` shows `uses_git: true` |
| **7. LookML Model & Views** | Author views and model, map connection, validate, and run query | [references/lookml-model-create.md](references/lookml-model-create.md) & [references/lookml-style-guide.md](references/lookml-style-guide.md) | `validate_project` passes (0 errors) and inline query returns rows |
| **8. Dashboard & Sync Loop** | Author LookML dashboard, import as UDD, verify tile queries, and iterate | [references/looker-dashboard-create.md](references/looker-dashboard-create.md) | UDD imported, all element `query_id` runs succeed, user approves |

---

## Orchestration Rules & Guardrails

1. **Strict Sequential Execution:** Never skip a step or execute steps out of order (`Pre-flight -> Discovery -> CLI -> Auth -> Connect -> Project -> Model -> Dashboard`).
2. **Fail Fast:** Halt immediately if any step or verification command fails, explain the cause clearly, and resolve it before continuing.
3. **Interactive Checkpoints:**
   - **Step 2 (Discovery):** Stop and wait for the user's interview answers before running any `bq` commands, and confirm the proposed dashboard goal before Step 3.
   - **Step 4 (CLI Auth):** Present the OAuth login URL and wait for the user to complete browser authorization (or paste the headless redirect URL).
   - **Step 8 (Dashboard):** Present the imported User-Defined Dashboard (UDD) URL and iterate on user feedback via `looker-cli dashboard sync lookml`.

---

## Educational Transparency Guidelines

Because the user may be new to Looker, act as a transparent, concise guide throughout the workflow:

- **Narrate Actions:** Before running major commands or creating files, briefly state what you are doing and why.
- **Explain Core Concepts in 1–2 Sentences:** When completing milestones (views, Explores, model connection mapping, UDD import), briefly explain what each construct does (e.g., views map to BigQuery tables; Explores define how views join together).
- **Prioritize Momentum:** Keep explanations crisp and actionable so the user reaches their working dashboard quickly.
