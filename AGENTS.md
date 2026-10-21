# Contributor Guide for Coding Agents (`AGENTS.md`)

This repository (`looker-open-source/looker-skills`) distributes official Looker agentic skills organized into domain-specific plugins under `plugins/<domain>/skills/`. Before creating, refactoring, or reviewing any skill in this repository, read and enforce the rules below.

---

## 1. Repository Directory Architecture

```text
looker-skills/
|-- AGENTS.md                          # Instructions for contributor coding agents
|-- .agents/skills/                    # Maintainer-only skills (never shipped to end users)
|-- _shared/                           # Canonical shared assets (no SKILL.md)
|   |-- references/                    # Shared markdown references injected via sync_shared.py
|   |-- scripts/                       # Shared utility scripts
|-- plugins/                           # Domain-scoped plugins
|   |-- looker-base/                   # CLI & MCP setup (mcp.json + base skills; required by all plugins)
|   |-- looker-lookml-modeling/        # LookML authoring, architecture, review, migration, optimization
|   |-- looker-onboarding-migration/   # Step-by-step developer onboarding orchestrator
|   |-- looker-operations/             # Instance administration, connections, audit, and health
|   |-- looker-apps-viz/               # Dashboards, custom visualizations, extensions, Data Apps
|   |-- looker-analytics-agents/       # Conversational Analytics (CA) agent creation & optimization
|-- experimental/                      # Stage 1 experimental skills (not in marketplace manifests)
|-- examples/                          # Sample LookML project for testing
|-- scripts/                           # Repository maintenance scripts (sync_shared.py, validate.py)
```

- **Unique Skill Names:** Every skill folder name must be globally unique across the repository (`lowercase-kebab-case`) and live in exactly one domain plugin (or `experimental/`).
- **Mandatory `looker-base` Dependency:** Every domain plugin depends on `looker-base`. Any skill that invokes Looker MCP tools or the Looker CLI must include the following one-line prerequisite check in its `SKILL.md`:
  > `If the Looker MCP tools or Looker CLI are unavailable, ask the user to install looker-base first.`

---

## 2. The Four Skill Consolidation Tests

A candidate topic qualifies as a standalone skill (with its own `SKILL.md`) **only** if it passes all four tests below:

1. **Workflow vs. Syntax:** It defines a multi-step workflow or decision rules, not merely the syntax for a single construct.
2. **Distinct Outcome:** It produces a result that no other skill in the repository produces.
3. **Unambiguous User Trigger:** Users ask for it directly in words that do not collide with a sibling skill in the same domain plugin.
4. **Not a Reference File:** Its content does not fit better as a modular file inside `references/` of a broader skill (such as `lookml-author` or `looker-developer-onboarding`).

---

## 3. Frontmatter Specification (`agentskills.io`)

Every `SKILL.md` must begin with YAML frontmatter conforming to the schema below (no XML angle brackets `< >` inside frontmatter values):

```yaml
---
name: <skill-folder-name>
description: >-
  <What the skill does + explicit "Use when..." positive triggers and "Do not
  use for..." negative routing boundaries. Maximum 1024 characters.>
license: Apache-2.0
compatibility: Requires looker-base (Looker MCP and looker-cli).
metadata:
  version: 0.1.0          # Semantic Versioning 2.0.0: 0.x.x for experimental/preview; >= 1.0.0 for ga
  domain: <plugin-name>   # Must match the parent folder under plugins/
  status: preview         # experimental | preview | ga
  usage-interface: looker-mcp looker-cli
  publisher: google
  shared-refs: <optional space-separated list of _shared/references/ names without .md>
---
```

---

## 4. Progressive Disclosure & Minimal Footprint Rules

- **`SKILL.md` Line Limit (`<= 150` lines):** Keep `SKILL.md` focused on workflow steps, behavioral guardrails, and links to one-level-deep `references/*.md` files. Do not embed code blocks longer than 5 lines in `SKILL.md`.
- **Reference File Line Limit (`<= 250` lines):** Place detailed templates, schemas, and API payload examples inside `references/*.md` (maximum 250 lines per file).
- **No Root `README.md` Inside Skill Folders:** Do not place a `README.md` at the root of a skill folder. If human-facing documentation is needed for a skill, place it at `references/guide.md`.
- **Shared References (`_shared/`):** Never manually duplicate shared setup or best-practice guides across skills. Place canonical shared files in `_shared/references/<name>.md`, declare `<name>` in `metadata.shared-refs`, and run `python3 scripts/sync_shared.py`.

---

## 5. Validation & Synchronization Commands

Before opening or updating a pull request, always run:

```bash
# 1. Synchronize _shared/ references into skills declaring metadata.shared-refs
python3 scripts/sync_shared.py

# 2. Validate frontmatter, line limits, unique names, and link integrity
python3 scripts/validate.py
```
