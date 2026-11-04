# Profiles, Session Management, Discovery, and API Payloads (`looker-cli`)

## 1. Managing Profiles

Profiles store connection configurations (host, port, credentials, tokens) for different Looker instances in `~/.config/looker-cli/config.yaml`.

### Adding & Listing Profiles
```bash
# Add a profile (optional flags: --client-id, --client-secret, --token, --refresh-token)
looker-cli profile add staging --host staging.looker.mycompany.com --port 443

# List all profiles (* denotes active default profile)
looker-cli profile ls
```

### Setting, Overriding, and Deleting Profiles
```bash
# Set default profile
looker-cli profile use prod

# Override profile for a single command without changing default
looker-cli user me --profile prod
looker-cli project ls --profile dev

# Remove a stored profile
looker-cli profile rm staging
```

---

## 2. Persistent Sessions (`session`)

`looker-cli` supports persistent authentication sessions so commands can execute without re-authenticating on every request.

```bash
# Authenticate using configured API credentials
looker-cli session login

# Interactive OAuth 2.0 PKCE browser login
looker-cli session login --oauth

# Output token to stdout instead of persisting to config.yaml
looker-cli session login --text

# Check active session status (user ID, workspace, expiration)
looker-cli session get

# Switch workspace between personal development ('dev') and 'production'
looker-cli session update --workspace-id dev
looker-cli session update --workspace-id production

# Invalidate and end active session
looker-cli session logout
```

---

## 3. Command Discovery (`meta tree` & `meta search`)

### Visualizing Command Subtrees (`meta tree`)
```bash
# Full command tree
looker-cli meta tree

# Filter tree to a specific resource noun
looker-cli meta tree --noun project

# Output command subtree as JSON
looker-cli meta tree --noun query --output json
```

Sample output for `looker-cli meta tree --noun project`:
```text
project
├── branch
├── cat
├── checkout
├── create
├── deploy
│   └── key
├── directory
│   ├── create
│   ├── ls
│   └── rm
├── file
│   ├── cat
│   ├── create
│   ├── ls
│   ├── rm
│   └── update
├── import
├── ls
├── update
└── validate
```

### Searching Commands by Keyword (`meta search`)
```bash
looker-cli meta search project
looker-cli meta search user
```

Sample output:
```text
Found 63 matching commands:
  looker-cli api project create_project - Create Project
  looker-cli api project deploy_to_production - Deploy To Production
  looker-cli api project validate_project - Validate Project
  looker-cli project create - Create a new project
  looker-cli project validate - Validate a project
```

---

## 4. Inspecting API Request Bodies (`--describe-body` & `--template`)

Low-level REST API endpoints are exposed under `looker-cli api <group> <endpoint>`.

### Inspecting Request JSON Schema (`--describe-body`)
Lists all allowable parameters, types, descriptions, nullable flags, and allowed enum values (`x-looker-values`):
```bash
looker-cli api project create_project --describe-body
```

```json
{
  "properties": {
    "name": {
      "description": "Project display name",
      "type": "string",
      "x-looker-nullable": false
    },
    "pull_request_mode": {
      "description": "The git pull request policy for this project.",
      "type": "string",
      "x-looker-nullable": false,
      "x-looker-values": ["off", "links", "recommended", "required"]
    }
  }
}
```

### Generating & Submitting Payload Templates (`--template`)
1. **Generate skeleton JSON template:**
   ```bash
   looker-cli api project create_project --template > new_project.json
   ```
2. **Populate required fields in `new_project.json`:**
   ```json
   {
     "name": "my_new_project",
     "pull_request_mode": "recommended"
   }
   ```
3. **Execute API request with `--body`:**
   ```bash
   looker-cli api project create_project --body new_project.json
   ```
