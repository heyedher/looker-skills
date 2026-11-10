# Step 6: Setting Up Looker Project & Git (`looker-project-setup`)

Creates a new LookML project in the development workspace and configures it with a local bare Git repository on the Looker server so onboarding can proceed immediately without external Git hosting setup.

## Prerequisites

- `looker-cli` is installed and authenticated (Steps 3 & 4).
- The BigQuery connection has been created and verified (Step 5: [connecting-looker-to-bigquery.md](connecting-looker-to-bigquery.md)).

---

## Instructions

### 1. Switch Session to the Development Workspace

Creating or updating LookML projects requires the `dev` workspace. Chain `session update dev` with project commands to guarantee dev workspace persistence:

```bash
looker-cli session update dev
```

---

### 2. Create the LookML Project

1. Write the project creation payload to `/tmp/project_create.json` using a unique, URL-safe `lowercase_snake_case` name for `{project_id}` (e.g., `ecommerce_analytics`):
   ```json
   {
     "name": "{project_id}"
   }
   ```
2. Import the new project in the `dev` workspace:
   ```bash
   looker-cli session update dev && looker-cli project import /tmp/project_create.json
   ```

---

### 3. Configure a Local Bare Git Repository

1. Write the Git configuration payload to `/tmp/project_git.json`:
   ```json
   {
     "git_service_name": "bare"
   }
   ```
2. Update the project to initialize the server-side bare Git repository:
   ```bash
   looker-cli session update dev && looker-cli project update {project_id} /tmp/project_git.json
   ```

---

### 4. Verify Project & Git Configuration

Retrieve the project configuration to confirm Git is active:

```bash
looker-cli project cat {project_id}
```

Confirm that the JSON output shows:
- `"uses_git": true`
- `"git_remote_url"` is populated (e.g., `"../../bare_models/{project_id}.git"`).

> **Note:** If `looker-cli project cat {project_id}` returns a transient `400` error immediately after initializing bare Git, wait 2–3 seconds for server propagation and retry.
