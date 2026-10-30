# Looker Developer Skills Repository

Official agentic skills for Looker, organized into **6 domain-scoped plugins** under `plugins/` to help AI coding assistants (**Gemini CLI**, **Claude Code**, **Cursor**, **GitHub Copilot**, **Antigravity**, and **Codex**) build, audit, optimize, and operate LookML projects, dashboards, extensions, and Conversational Analytics agents without saturating context windows.

> Migrating from `v0.4.x` (`skills/*`)? See [MIGRATION.md](MIGRATION.md) for the complete consolidation map and backwards-compatible `.agents/skills/` paths.

---

## Domain Plugin Catalog

Install only the domain plugin(s) relevant to your workflow (every domain plugin builds on `looker-base`):

| Domain Plugin | Version | Status | Included Skills | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **[looker-base](plugins/looker-base/plugin.json)** | `1.0.0` | GA | `using-looker-mcp`, `looker-cli-run` (+ `mcp.json`) | Looker MCP server configuration and `looker-cli` execution prerequisites required by all domain plugins. |
| **[looker-lookml-modeling](plugins/looker-lookml-modeling/plugin.json)** | `1.0.0` | GA | `lookml-author`, `looker-architect`, `lookml-performance-optimizer`, `lookml-reviewer`, `lookml-dialect-migration` | Authoring LookML constructs, scaffolding raw/refined enterprise projects, tuning SQL/PDT/datagroup performance, reviewing PR diffs, and migrating SQL dialects. |
| **[looker-onboarding-migration](plugins/looker-onboarding-migration/plugin.json)** | `1.0.0` | GA | `looker-developer-onboarding` | End-to-end guided developer onboarding from BigQuery connection setup through first LookML model and dashboard. |
| **[looker-operations](plugins/looker-operations/plugin.json)** | `1.0.0` | GA | `looker-audit` | Instance-wide System Activity governance, unused content cleanup, and datagroup health auditing. |
| **[looker-apps-viz](plugins/looker-apps-viz/plugin.json)** | `0.1.0` | Preview | `looker-custom-viz`, `looker-dashboards`, `looker-extension` | Building native LookML dashboards, custom visualizations, and Looker Extension SDK applications. |
| **[looker-analytics-agents](plugins/looker-analytics-agents/plugin.json)** | `0.1.0` | Preview | `looker-ca-agent-optimize`, `looker-ca-agent-create` | Creating, auditing, and optimizing Looker Conversational Analytics (CA) Standalone and Dashboard Agents. |

---

## Installation & Usage

### 1. Install via `npx skills add` (Recommended)

Install individual skills or the full catalog into your workspace:

```bash
# Install all Looker skills
npx skills add looker-open-source/looker-skills

# Or install a specific skill (plus looker-base prerequisites)
npx skills add looker-open-source/looker-skills --skill looker-architect
```

### 2. Install Domain Plugins in Claude Code, Cursor, or GitHub Copilot

This repository ships multi-client marketplace manifests (`.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json`, and `.github/plugin/marketplace.json`) so you can install only the domain plugins you need:

```bash
git clone https://github.com/looker-open-source/looker-skills.git

# Claude Code: load a single domain plugin + looker-base
claude --plugin-dir ./looker-skills/plugins/looker-base --plugin-dir ./looker-skills/plugins/looker-lookml-modeling

# Or register the repository marketplace persistently
claude plugin install ./looker-skills
```

### 3. Antigravity CLI

```bash
agy plugin install https://github.com/looker-open-source/looker-skills
```

### 4. Codex

```bash
curl -sSL -o codex-install.sh https://raw.githubusercontent.com/looker-open-source/looker-skills/main/codex-install.sh && bash codex-install.sh
```

### 5. Copy Skills into Current Workspace via npm (`@looker/looker-skills`)

```bash
npx @looker/looker-skills
```

---

## Skill Reference by Domain

### 1. Base Infrastructure (`plugins/looker-base`)
* **`using-looker-mcp`**: Configures and operates the prebuilt Looker MCP server (`@googleapis/mcp-toolbox`).
* **`looker-cli-run`**: Installs, authenticates, and executes `looker-cli` commands against Looker instances.

### 2. LookML Modeling & Performance (`plugins/looker-lookml-modeling`)
* **`lookml-author`**: Unified LookML authoring workflow covering models, explores, joins, views, derived tables, fields, Liquid, sets, refinements, access grants, data tests, and style conventions.
* **[looker-architect](plugins/looker-lookml-modeling/skills/looker-architect/SKILL.md)**: End-to-end greenfield scaffolding and brownfield modernization enforcing raw/refined view separation, functional field sequencing, Period-over-Period KPI engines, manifest visual drills, native tabbed dashboards, PK unit tests, and MCP self-healing SQL verification.
* **[lookml-performance-optimizer](plugins/looker-lookml-modeling/skills/lookml-performance-optimizer/SKILL.md)**: Audits and tunes slow SQL queries, warehouse scan costs, ETL-aligned `datagroup` caching, SARGable dimensions, join pruning, and incremental PDT cold-start materializations.
* **`lookml-reviewer`**: Structured code review workflow for LookML pull requests and semantic changes.
* **`lookml-dialect-migration`**: Translates warehouse SQL dialects across LookML projects (including Snowflake to BigQuery Standard SQL).

### 3. Developer Onboarding (`plugins/looker-onboarding-migration`)
* **`looker-developer-onboarding`**: Orchestrator guiding new developers step-by-step through preflight checks, schema exploration, BigQuery connection creation, project setup, LookML modeling, and dashboard creation.

### 4. Operations & Governance (`plugins/looker-operations`)
* **`looker-audit`**: Audits Looker instances via System Activity for dashboard performance bottlenecks, excessive table calculations, unused content, and datagroup health.

### 5. Dashboards, Visualizations & Extensions (`plugins/looker-apps-viz` — Preview)
* **`looker-dashboards`**: Designs and configures Looker dashboards and visualization types.
* **`looker-custom-viz`**: Builds custom JavaScript/TypeScript visualizations using the Looker Visualization API.
* **`looker-extension`**: Scaffolds and develops embedded applications with the Looker Extension SDK.

### 6. Conversational Analytics Agents (`plugins/looker-analytics-agents` — Preview)
* **`looker-ca-agent-optimize`**: Audits and optimizes existing Looker Conversational Analytics Standalone and Dashboard Agents across zero-token `Audit` mode and Side-by-Side (SxS) `Optimize` mode.
* **`looker-ca-agent-create`**: Designs and deploys new Standalone (Explore-backed) and Dashboard-backed Conversational Analytics Agents with 4-part structured instructions and verified golden queries.

---

## Contributing & Repository Validation

See [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for skill authoring standards and consolidation rules. Before submitting a pull request, run:

```bash
python3 scripts/sync_shared.py
python3 scripts/build_release.py
python3 scripts/validate.py
```
