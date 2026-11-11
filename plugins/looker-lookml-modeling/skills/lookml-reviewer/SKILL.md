---
name: lookml-reviewer
description: >-
  Review and audit a LookML codebase or specific file on a remote Looker
  instance for compliance with LookML best practices, LAMS style rules, and
  Conversational Analytics readiness using looker-cli. Use when asked to review,
  audit, check, or critique LookML code or a LookML project branch. Do not use
  for authoring new LookML from scratch (use lookml-author or looker-architect)
  or auditing instance-wide System Activity and PDT health (use looker-audit).
license: Apache-2.0
compatibility: Requires looker-base (Looker MCP and looker-cli).
metadata:
  version: 1.0.0
  domain: looker-lookml-modeling
  status: ga
  usage-interface: looker-cli
  publisher: google
---

# LookML Code Reviewer (`lookml-reviewer`)

Performs a structured code audit on remote LookML files or entire Looker projects against official LookML best practices, LAMS conventions, maintainability standards, and Conversational Analytics readiness using `looker-cli`.

> **Prerequisite:** If the Looker MCP tools or Looker CLI are unavailable, ask the user to install `looker-base` first.

---

## Task-Gated Reference Routing (Read Only What You Need)

| Active Step / Need | Reference File | Line Range |
| :--- | :--- | :--- |
| Human usage overview & required inputs | [references/guide.md](references/guide.md) | `L1-L44` |
| Step 4: Core LookML Do's & Don'ts (PKs, includes, joins) | [references/lookml-dos-and-donts.md](references/lookml-dos-and-donts.md) | `L1-L55` |
| Step 4: LAMS Naming & Structural Rules (`K*`, `F*`, `E*`, `T*`) | [references/lams-style-guide.md](references/lams-style-guide.md) | `L1-L110` |
| Step 4: Sustainable & Maintainable LookML Architecture | [references/sustainable-maintainable-lookml.md](references/sustainable-maintainable-lookml.md) | `L1-L108` |
| Step 4: Conversational Analytics Readiness (`description`, `tags`) | [references/conversational-analytics-best-practices.md](references/conversational-analytics-best-practices.md) | `L1-L71` |

---

## Execution Workflow

1. **Step 1 — Pre-flight CLI & Auth Verification:**
   - Run `looker-cli --help`. If missing, halt and ask the user to install `looker-cli` (`looker-base`).
   - Run `looker-cli user me`. If unauthenticated, halt and instruct the user to configure their profile (`looker-cli profile add default --host <host> --port 443 && looker-cli profile use default`) and log in (`looker-cli session login --oauth` or `--client-id` / `--client-secret`).

2. **Step 2 — Understand Scope & Validate Branch (No Branch Creation):**
   - Require the **Looker Instance URL**, **Project Name (`<project_id>`)**, **Branch Name (`<branch_name>`)**, and optional **Target File (`<file_path>`)**. If Instance URL, Project Name, or Branch Name was not provided, ask the user before proceeding.
   - Switch to dev workspace and list branches:
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

4. **Step 4 — Audit Against Bundled Reference Guides:**
   - Evaluate retrieved LookML against [references/lookml-dos-and-donts.md](references/lookml-dos-and-donts.md), [references/lams-style-guide.md](references/lams-style-guide.md), [references/sustainable-maintainable-lookml.md](references/sustainable-maintainable-lookml.md), and [references/conversational-analytics-best-practices.md](references/conversational-analytics-best-practices.md).
   - Check primary keys (`primary_key: yes`), explicit `relationship` and `sql_on`, field substitution (`${field}`), naming conventions, `description` coverage, count filters, datagroups, and CA readiness.

5. **Step 5 — Compile & Print the Review Report Directly in Chat:**
   - **Summary:** Overall health of the file or codebase, naming instance, project, branch, and scope.
   - **Strengths:** Bulleted list of well-implemented LookML patterns.
   - **Improvement Points (Organized by File):**
     - Describe each violation concisely (do not copy-paste full rule definitions).
     - Provide concrete **Before** and **After** LookML code snippets.
     - Include exact file path, line numbers (`views/order_items.view.lkml:L16-L19`), and direct Looker IDE URL (`<instance_url>/projects/<project_id>/files/<file_path>`).
