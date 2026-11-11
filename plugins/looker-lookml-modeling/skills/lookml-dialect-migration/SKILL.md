---
name: lookml-dialect-migration
description: >-
  Audit and migrate LookML SQL expressions across database dialects (such as
  converting Snowflake SQL to BigQuery Standard SQL) on a Looker project using
  looker-cli. Use when asked to convert Snowflake-specific SQL syntax in LookML
  files to BigQuery syntax, audit a project for dialect incompatibilities, or
  propose SQL dialect migrations. Do not use for general LookML style reviews
  (use lookml-reviewer) or authoring new LookML constructs from scratch (use
  lookml-author).
license: Apache-2.0
compatibility: Requires looker-base (Looker MCP and looker-cli).
metadata:
  version: 1.0.0
  domain: looker-lookml-modeling
  status: ga
  usage-interface: looker-cli
  publisher: google
---

# LookML SQL Dialect Migration (`lookml-dialect-migration`)

Audits LookML files (`sql`, `sql_table_name`, `derived_table`, `sql_on`, `sql_always_where`, `sql_where`, `sql_trigger_value`) for source-dialect SQL syntax and generates production-ready target-dialect equivalents (including full Snowflake-to-BigQuery Standard SQL transition rules) using `looker-cli`.

> **Prerequisite:** If the Looker MCP tools or Looker CLI are unavailable, ask the user to install `looker-base` first.

---

## Task-Gated Reference Routing (Read Only What You Need)

| Active Step / Need | Reference File | Line Range |
| :--- | :--- | :--- |
| Human usage overview & required inputs | [references/guide.md](references/guide.md) | `L1-L42` |
| Step 4: Snowflake-to-BigQuery SQL function & syntax mappings | [references/snowflake-to-bigquery.md](references/snowflake-to-bigquery.md) | `L1-L81` |

---

## Execution Workflow

1. **Step 1 — Pre-flight CLI & Auth Verification:**
   - Run `looker-cli --help`. If missing, halt and ask the user to install `looker-cli` (`looker-base`).
   - Run `looker-cli user me`. If unauthenticated, halt and instruct the user to configure their profile (`looker-cli profile add default --host <host> --port 443 && looker-cli profile use default`) and log in (`looker-cli session login --oauth` or `--client-id` / `--client-secret`).

2. **Step 2 — Understand Scope & Validate Branch (No Branch Creation):**
   - Require the **Looker Instance URL**, **Project Name (`<project_id>`)**, **Branch Name (`<branch_name>`)**, and optional **Target File (`<file_path>`)**. If Instance URL, Project Name, or Branch Name was not provided, ask the user before proceeding.
   - Switch to dev workspace and list existing branches:
     ```bash
     looker-cli session update dev && looker-cli project branch <project_id> --all
     ```
   - **Never create a branch.** If the user requested `master` and only `main` exists (or vice versa), map to the existing default branch and inform the user. If the branch does not exist, halt, list available branches, and ask for clarification.

3. **Step 3 — Checkout & Retrieve LookML Files via `looker-cli`:**
   - Checkout the target branch:
     ```bash
     looker-cli project checkout <project_id> <branch_name>
     ```
     *(If checkout fails due to uncommitted local changes in the dev workspace, halt and ask the user to commit or discard their changes in Looker first).*
   - List project files:
     ```bash
     looker-cli project file ls <project_id>
     ```
   - **Single-File Mode:** Verify `<file_path>` exists in the listing (halt and list candidates if missing) and fetch it:
     ```bash
     looker-cli project file cat <project_id> <file_path>
     ```
   - **Full-Project Mode:** Retrieve each LookML file (`*.model.lkml`, `*.explore.lkml`, `*.view.lkml`, `manifest.lkml`).

4. **Step 4 — Scan for Dialect-Specific SQL Syntax:**
   - Audit all SQL blocks against [references/snowflake-to-bigquery.md](references/snowflake-to-bigquery.md).
   - Flag incompatible Snowflake constructs (`IFF`, `NVL`, `ZEROIFNULL`, `DIV0`, `DECODE`, `DATEADD`, `DATEDIFF`, `DATE_TRUNC` argument order, `SPLIT_PART`, `LEN`, `CHARINDEX`, `ILIKE` / `NOT ILIKE`, `ILIKE ANY`, `::` casting, `:` semi-structured access, `LATERAL FLATTEN`, and double-quoted column identifiers `${TABLE}."COLUMN_NAME"`).
   - Preserve syntax already natively valid in BigQuery Standard SQL (such as `QUALIFY` and `COALESCE`).

5. **Step 5 — Compile & Print the Migration Report Directly in Chat:**
   - **Summary:** Instance, project, branch, and file-by-file compatibility status table.
   - **Proposed Conversions (Organized by File):**
     - Explain each incompatible SQL construct and its BigQuery Standard SQL replacement.
     - Provide concrete **Before (Snowflake)** and **After (BigQuery)** LookML/SQL snippets.
     - Include exact file path, line numbers (`views/orders.view.lkml:L27-L44`), and direct Looker IDE URL (`<instance_url>/projects/<project_id>/files/<file_path>`).
