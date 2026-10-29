# Migration Guide: Flat `skills/` (`v0.4.x`) to Domain Plugins

To reduce agent context bloat and prevent routing collisions when installing the full repository, `looker-open-source/looker-skills` reorganized its flat `24`-skill `skills/` directory into **6 domain-scoped plugins** under `plugins/<domain>/skills/`.

---

## 1. Backwards Compatibility (`.agents/skills/` & `npx @looker/looker-skills`)

* **Flat Discovery Preserved:** `.agents/skills/` continues to expose flat relative symlinks for every published skill (`python3 scripts/build_release.py`), so tools that scan `.agents/skills/<skill-name>/SKILL.md` (including `npx skills add` and Codex) continue to work without path changes for consolidated skill names.
* **CLI Copy Utility Preserved:** Running `npx @looker/looker-skills` automatically discovers skills under `plugins/*/skills/*` and copies them into your workspace's `.agents/skills/` directory.
* **Domain-Scoped Installation (Recommended):** In Claude Code, Cursor, and GitHub Copilot, you can now install `looker-base` plus only the specific domain plugin(s) your team uses rather than loading every skill into every prompt.

---

## 2. Complete Skill Migration & Consolidation Map

| Legacy Path (`v0.4.x`) | New Location | Change Summary |
| :--- | :--- | :--- |
| `skills/looker-mcp-skill/` | `plugins/looker-base/skills/using-looker-mcp/` | Moved into mandatory `looker-base` plugin alongside `mcp.json` and renamed to `using-looker-mcp`. |
| `skills/using-looker-cli/` | `plugins/looker-base/skills/looker-cli-run/` | Moved into `looker-base` and renamed to `looker-cli-run`. |
| `skills/installing-looker-cli/` | `_shared/references/looker-cli-setup.md` | Extracted as a shared reference bundled into CLI-enabled skills via `metadata.shared-refs`. |
| `skills/authenticating-looker-cli/` | `_shared/references/looker-cli-auth.md` | Extracted as a shared reference bundled into CLI-enabled skills via `metadata.shared-refs`. |
| `skills/lookml-model/`<br>`skills/lookml-explore/`<br>`skills/lookml-view/`<br>`skills/lookml-fields/`<br>`skills/lookml-liquid/`<br>`skills/lookml-sets/`<br>`skills/lookml-refinements/`<br>`skills/lookml-access-grants/`<br>`skills/lookml-tests/`<br>`skills/lookml-modeling-guidelines/` | `plugins/looker-lookml-modeling/skills/lookml-author/` | **10-to-1 Consolidation:** Unified into a single `lookml-author` skill with modular construct guides under `lookml-author/references/*.md`. |
| `skills/looker-architect/` | `plugins/looker-lookml-modeling/skills/looker-architect/` | Moved to `looker-lookml-modeling`; slimmed `SKILL.md` for progressive disclosure and moved root `README.md` to `references/guide.md`. |
| `skills/looker-performance-optimizer/` | `plugins/looker-lookml-modeling/skills/lookml-performance-optimizer/` | Moved to `looker-lookml-modeling` and **renamed** to `lookml-performance-optimizer` to disambiguate LookML/SQL query optimization from Conversational Analytics agent optimization (`looker-ca-agent-optimize`). |
| `skills/lookml-reviewer/` | `plugins/looker-lookml-modeling/skills/lookml-reviewer/` | Moved to `looker-lookml-modeling`. |
| `skills/snowflake-to-bigquery-converter/` | `plugins/looker-lookml-modeling/skills/lookml-dialect-migration/` | Moved to `looker-lookml-modeling` and generalized as `lookml-dialect-migration` (`references/snowflake-to-bigquery.md`). |
| `skills/looker-developer-onboarding/`<br>`skills/onboarding-preflight-check/`<br>`skills/exploring-data-for-looker/`<br>`skills/connecting-looker-to-bigquery/`<br>`skills/setting-up-looker-project/`<br>`skills/creating-lookml-model/`<br>`skills/creating-looker-dashboard/` | `plugins/looker-onboarding-migration/skills/looker-developer-onboarding/` | **7-to-1 Consolidation:** Step-level onboarding skills folded into modular step guides under `looker-developer-onboarding/references/*.md` (`preflight_check.sh` moved to `_shared/scripts/`). |
| `skills/looker-audit/` | `plugins/looker-operations/skills/looker-audit/` | Moved to `looker-operations`. |
| *(New)* | `plugins/looker-apps-viz/skills/{looker-dashboards,looker-custom-viz,looker-extension}/` | New Preview domain plugin for Looker dashboards, custom visualizations, and Extension SDK apps. |
| *(New)* | `plugins/looker-analytics-agents/skills/{looker-ca-agent-optimize,looker-ca-agent-create}/` | New Preview domain plugin for auditing, optimizing, and creating Looker Conversational Analytics (CA) agents. |
| Root sample LookML files (`views/`, `explores/`, `dashboards/`, `tests/`, `manifest.lkml`, `enterprise_analytics.model.lkml`) | `examples/` | Relocated out of the repository root into `examples/`. |

---

## 3. Updating Existing Local Installations

If you previously copied the flat `24` skills into your project's `.agents/skills/` folder:

1. Remove superseded construct/step skill folders (`lookml-model`, `lookml-explore`, `lookml-view`, `lookml-fields`, `lookml-liquid`, `lookml-sets`, `lookml-refinements`, `lookml-access-grants`, `lookml-tests`, `lookml-modeling-guidelines`, `installing-looker-cli`, `authenticating-looker-cli`, `onboarding-preflight-check`, `exploring-data-for-looker`, `connecting-looker-to-bigquery`, `setting-up-looker-project`, `creating-lookml-model`, `creating-looker-dashboard`, and `looker-performance-optimizer`).
2. Reinstall using `npx skills add looker-open-source/looker-skills` or `npx @looker/looker-skills --override`, or switch to domain-scoped plugin loading (`looker-base` + your target domain plugin).
