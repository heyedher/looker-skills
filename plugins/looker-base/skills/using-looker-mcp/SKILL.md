---
name: using-looker-mcp
description: >-
  Connect to, configure, and use the Looker Model Context Protocol (MCP) Server
  across Looker-managed and standalone MCP Toolbox deployments. Use when
  setting up Looker MCP client configurations, configuring OAuth PKCE
  authentication, or selecting Looker MCP tools for querying, discovery,
  dashboards, LookML authoring, and diagnostics. Do not use for Looker CLI
  terminal commands (use looker-cli-run).
license: Apache-2.0
compatibility: Requires looker-base (Looker MCP and looker-cli).
metadata:
  version: 1.0.0
  domain: looker-base
  status: ga
  usage-interface: looker-mcp
  publisher: google
---

# Using Looker MCP (`using-looker-mcp`)

This skill guides AI assistants and developers through connecting to, authenticating with, and invoking the **Looker Model Context Protocol (MCP) Server** to query semantic models, inspect metadata, manage LookML projects, and run instance diagnostics.

> **Prerequisite:** If the Looker MCP tools or Looker CLI are unavailable, ask the user to install `looker-base` first.

---

## Workflow

### Step 1: Select the MCP Deployment Mode

Determine whether the target Looker environment uses the built-in managed endpoint or a standalone MCP Toolbox server:

1. **Looker-Managed MCP Server (Recommended for Looker Core & Cloud):**
   - Built directly into the Looker instance at `https://<YOUR_LOOKER_INSTANCE_URL>/mcp`.
   - Enabled in **Admin Panel > Platform > MCP** (`Enable MCP Server: On`).
2. **Local / Standalone MCP Server (`@google/mcp-toolbox`):**
   - Used for customer-hosted instances, local STDIO integrations, or Cloud Run deployments.
   - Launch via `npx @google/mcp-toolbox --prebuilt=looker,looker-dev` or the official Docker image (`us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest`).
   - Requires `LOOKER_BASE_URL`, `LOOKER_CLIENT_ID`, and `LOOKER_CLIENT_SECRET` environment variables.

### Step 2: Configure Authentication & Client `mcp.json`

1. For **Looker-Managed MCP**, register an OAuth client application (`POST /api/4.0/oauth_client_apps/{client_guid}`) and authenticate via OAuth 2.0 PKCE or Bearer tokens.
2. Add the Looker server entry to your client configuration (see bundled [mcp.json](../../mcp.json) in `looker-base` or the detailed examples in [references/oauth-and-client-setup.md](references/oauth-and-client-setup.md)).

### Step 3: Select and Execute Looker MCP Tools

Choose the appropriate MCP tool category for your task (full 45-tool reference in [references/mcp-tools-catalog.md](references/mcp-tools-catalog.md)):

- **Data & Query Execution:** `query`, `query_sql`, `query_url`, `run_look`, `run_dashboard`
- **Discovery & Metadata Catalog:** `get_models`, `get_explores`, `get_dimensions`, `get_measures`, `get_filters`, `get_parameters`, `get_connections`, `get_connection_databases`, `get_connection_schemas`, `get_connection_tables`, `get_connection_table_columns`
- **Dashboards & Content Creation:** `get_looks`, `get_dashboards`, `make_look`, `make_dashboard`, `add_dashboard_element`, `add_dashboard_filter`, `generate_embed_url`
- **LookML Project Development:** `dev_mode`, `get_projects`, `get_project_directories`, `get_project_files`, `get_project_file`, `create_project_file`, `update_project_file`, `delete_project_file`, `create_project_directory`, `delete_project_directory`, `create_view_from_table`, `validate_project`, `get_lookml_tests`, `run_lookml_tests`
- **Git Version Control:** `get_git_branch`, `list_git_branches`, `create_git_branch`, `switch_git_branch`, `delete_git_branch`
- **Diagnostics Utilities:** `health_pulse`, `health_analyze`, `health_vacuum`

---

## Security & Operational Guardrails

1. **User Scope Enforcement:** User-level Access Grants, Model Sets, and Row-Level Security (RLS) are enforced when authenticating via user-scoped OAuth on the Looker-Managed MCP Server.
2. **Static Credential Warning:** Running a shared standalone MCP server with static `LOOKER_CLIENT_ID` and `LOOKER_CLIENT_SECRET` executes all tool calls under that single credential pair, which can bypass individual user row-level security.
3. **Development Mode Isolation:** Always call `dev_mode` (`true`) before creating, updating, or deleting LookML project files so changes stay isolated to the developer branch.

---

## Reference Documentation

- [OAuth PKCE & Client Configuration Guide](references/oauth-and-client-setup.md): Step-by-step OAuth app registration, PKCE token exchange, and IDE/agent `mcp.json` templates.
- [Looker MCP Tools Catalog](references/mcp-tools-catalog.md): Complete 45-tool directory across all 6 functional areas.
