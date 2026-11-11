---
name: looker-audit
description: >-
  Audits a Looker instance for performance, governance, and cleanup
  opportunities using looker-cli and System Activity. Use when analyzing
  dashboard performance, identifying LookML anti-patterns, checking for
  excessive table calculations or merged queries, auditing PDT and datagroup
  health, or finding unused content and schedules. Do not use for general Looker
  onboarding (use looker-developer-onboarding) or optimizing Conversational
  Analytics agents (use looker-ca-agent-optimize).
license: Apache-2.0
compatibility: Requires looker-base (Looker MCP and looker-cli).
metadata:
  version: 1.0.0
  domain: looker-operations
  status: ga
  usage-interface: looker-cli
  publisher: google
---

# Looker Instance Audit & Health Check (`looker-audit`)

Guides you through a comprehensive operational and architectural audit of a remote Looker instance using `looker-cli` (`health pulse`, API calls, and `system__activity` inline queries) to diagnose performance bottlenecks, PDT/datagroup failures, LookML anti-patterns, and content/schedule bloat.

> **Prerequisite:** If the Looker MCP tools or Looker CLI are unavailable, ask the user to install `looker-base` first.

---

## Rules of Engagement (Mandatory Guardrails)

1. **Strictly API/CLI Only (No Local Filesystem Scans):** Never use `find`, `grep`, `ls`, or local file search tools to look for LookML files. Always inspect remote projects via `looker-cli api project all_project_files [project_id]` and `looker-cli project file cat [project_id] [path]`.
2. **Immediate Action:** Execute your first `looker-cli` command in Step 1 without exploring local directories.
3. **50-View Scaling Guardrail:** Before looping over a project's LookML files, check its view count (`all_project_files`). If a project has **> 50 views**, ask the user which projects or files to prioritize before running file loops.
4. **Graceful Degradation & Anti-Hallucination:** Never guess data. If an API call returns `404` or fails, report the finding using the available identifiers (View Name, Model Name, Dashboard ID) and do not pivot to local filesystem searches.
5. **Exact Count Verification (No Limit Truncation):** Always run the paired `count` query (or pipe IDs to `jq 'length'`) so reported totals reflect the true instance count rather than a query `--limit`.
6. **Complete Checklist Coverage:** Execute all 5 audit categories unless the user explicitly scopes the request to a single area.

---

## Task-Gated Reference Routing (Read Only What You Need)

| Active Step / Audit Area | Reference File | Line Range |
| :--- | :--- | :--- |
| Step 1: High-level `looker-cli health pulse` commands | [references/system_activity_queries.md](references/system_activity_queries.md) | `L9-L21` |
| Step 2A: Dashboard & Look complexity (tile bloat, auto-refresh, dynamic fields, merged queries, avg runtime) | [references/system_activity_queries.md](references/system_activity_queries.md) | `L25-L69` |
| Step 2B: Slow queries (>10s), failed datagroups, failed PDTs & cache hit ratio | [references/system_activity_queries.md](references/system_activity_queries.md) | `L73-L103` |
| Step 2C: Inactive users, unused/draft content & schedule hotspots/failures | [references/system_activity_queries.md](references/system_activity_queries.md) | `L107-L143` |
| Step 3: Remote LookML static loop, 50-view guardrail & unused models/fields | [references/lookml_static_audit_and_reporting.md](references/lookml_static_audit_and_reporting.md) | `L7-L69` |
| Step 4: Audit report naming, High/Medium/Low priorities & Looker UI links | [references/lookml_static_audit_and_reporting.md](references/lookml_static_audit_and_reporting.md) | `L73-L108` |
| Remediation architecture (4-phase query lifecycle, PDTs, caching & joins) | [references/performance_audit_guide.md](references/performance_audit_guide.md) | `L1-L121` |

---

## Execution Workflow

1. **Step 0 — CLI Setup, Profile Selection & Authentication Check:**
   - Verify `which looker-cli || which looker` (if missing, halt and ask the user to install `looker-cli` via `looker-base`).
   - Select the target profile (`looker-cli profile ls` and `looker-cli profile use [profile]`) and verify active auth via `looker-cli user me` (if unauthorized, halt and instruct the user to authenticate via `looker-cli session login --oauth` or API keys).

2. **Step 1 — High-Level Health Pulse Check:**
   - Run the 5 `looker-cli health pulse` commands in [references/system_activity_queries.md](references/system_activity_queries.md) (`L9-L21`) to surface top slow dashboards, dashboard errors, slow Explores, schedule failures, and database connection issues.

3. **Step 2 — System Activity Root-Cause Drill-Down (Categories 1, 2, 3 & 5):**
   - Execute the `system__activity` inline JSON queries in [references/system_activity_queries.md](references/system_activity_queries.md) (`L25-L143`):
     - **Category 1 (Dashboards & Looks):** Tile bloat (`> 25` tiles), auto-refresh, dynamic fields (`> 2` per tile), merged queries, and top 10 slowest dashboards by average runtime.
     - **Category 2 (Query Performance):** Queries exceeding `10s` runtime over the past 30 days.
     - **Category 3 (Pipeline & Cache Health):** Failed datagroups, failed PDT builds in the past 24 hours (fetching failing view LookML to diagnose unscoped tables or broken triggers), and 30-day cache hit ratio (`target > 50%`).
     - **Category 5 (User, Content & Schedule Hygiene):** Inactive users (`> 90` days), unused dashboards/Looks (`>= 60` days, noting Annual/Quarterly reports), `test`/`copy`/`draft` content, hourly schedule hotspots, failing schedules, and orphaned schedules owned by disabled users.

4. **Step 3 — Remote LookML Code Quality & Unused Asset Scan (Category 4):**
   - Follow [references/lookml_static_audit_and_reporting.md](references/lookml_static_audit_and_reporting.md) (`L7-L69`) to map top-queried models to projects, enforce the **50-view scaling guardrail**, run `validate_project` and the single-pass `.lkml` inspection loop (checking wildcard includes, missing `primary_key: yes`, numeric ID dimensions, and hardcoded DB references), and identify models with `0` queries in 365 days and fields with `0` usage in 90 days.

5. **Step 4 — Compile Bespoke, Prioritized Audit Report:**
   - Follow [references/lookml_static_audit_and_reporting.md](references/lookml_static_audit_and_reporting.md) (`L73-L108`) and [references/performance_audit_guide.md](references/performance_audit_guide.md) to format `audit_report_[instance_name]_[timestamp].md` with exact item counts, named examples, **High / Medium / Low** priority tiers, actionable LookML snippets or `looker-cli` commands, and direct Looker UI hyperlinks.
