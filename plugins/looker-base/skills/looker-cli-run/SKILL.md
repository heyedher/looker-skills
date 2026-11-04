---
name: looker-cli-run
description: >-
  Install, authenticate, and execute commands with the Looker CLI (looker-cli)
  including profile management, persistent OAuth sessions, command discovery
  (meta tree and meta search), and API request payload inspection
  (--describe-body and --template). Use when interacting with a Looker instance
  via terminal commands or shell scripts. Do not use for Looker MCP server
  configuration (use using-looker-mcp).
license: Apache-2.0
compatibility: Requires looker-base (Looker MCP and looker-cli).
metadata:
  version: 1.0.0
  domain: looker-base
  status: ga
  usage-interface: looker-cli
  publisher: google
  shared-refs: looker-cli-setup looker-cli-auth
---

# Running Looker CLI (`looker-cli-run`)

This skill guides agents and developers through installing, authenticating, discovering commands, and executing Looker API operations via **`looker-cli`**.

> **Prerequisite:** If the Looker MCP tools or Looker CLI are unavailable, ask the user to install `looker-base` first.

---

## Workflow

### Step 1: Verify CLI Installation & Authentication

1. Check if `looker-cli` is installed in `PATH` by running `looker-cli --help`.
   - If missing, follow [references/looker-cli-setup.md](references/looker-cli-setup.md) to download and install the pre-compiled binary for the active OS.
2. Verify an active authenticated session exists with `looker-cli session get` or `looker-cli user me`.
   - If unauthenticated, follow [references/looker-cli-auth.md](references/looker-cli-auth.md) to configure a profile and complete `looker-cli session login --oauth`.

### Step 2: Manage Profiles & Workspace Context

Use named profiles in `~/.config/looker-cli/config.yaml` to target multiple Looker environments (`dev`, `staging`, `prod`) and switch between production and personal development workspaces (see [references/profiles-and-discovery.md](references/profiles-and-discovery.md)):

- **List or switch default profile:** `looker-cli profile ls` and `looker-cli profile use <name>`
- **Override profile per command:** Append `--profile <name>` to any command.
- **Toggle workspace context:** Run `looker-cli session update --workspace-id dev` before modifying LookML files, and `--workspace-id production` for production queries.

### Step 3: Discover CLI Commands & API Endpoints

Before guessing command syntax, use the built-in `meta` discovery subcommands:

- **Inspect command hierarchy:** `looker-cli meta tree --noun <resource>` (e.g., `project`, `dashboard`, `query`, `user`).
- **Search by keyword:** `looker-cli meta search <keyword>` to list both high-level CLI commands and low-level `looker-cli api <group> <endpoint>` operations.

### Step 4: Inspect & Submit API Request Payloads

When calling low-level `looker-cli api <group> <endpoint>` POST/PUT/PATCH endpoints:

1. **Inspect schema:** Run `looker-cli api <group> <endpoint> --describe-body` to view required fields, types, and `x-looker-values`.
2. **Generate skeleton:** Run `looker-cli api <group> <endpoint> --template` to generate a clean JSON payload template.
3. **Execute request:** Populate the JSON payload and pass `--body <payload.json>`.

---

## Quick Reference Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Add Profile** | `looker-cli profile add dev --host dev.looker.com --port 443` |
| **Set Default Profile** | `looker-cli profile use dev` |
| **Override Profile** | `looker-cli project ls --profile prod` |
| **OAuth PKCE Login** | `looker-cli session login --oauth` |
| **Switch to Dev Workspace** | `looker-cli session update --workspace-id dev` |
| **Command Tree by Noun** | `looker-cli meta tree --noun project` |
| **Search Commands** | `looker-cli meta search <keyword>` |
| **View Request Schema** | `looker-cli api <group> <endpoint> --describe-body` |
| **Generate JSON Template** | `looker-cli api <group> <endpoint> --template` |

---

## Reference Documentation

- [Looker CLI Setup Guide](references/looker-cli-setup.md): OS-specific installation instructions from GitHub Releases.
- [Looker CLI Authentication Guide](references/looker-cli-auth.md): OAuth PKCE browser login, headless callback flow, and privilege verification.
- [Profiles, Discovery & API Payloads](references/profiles-and-discovery.md): Detailed examples for profile management, persistent sessions, `meta` discovery, and `--describe-body`/`--template` workflows.
