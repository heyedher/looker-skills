# OAuth Authentication & MCP Client Configuration

## 1. Setting Up OAuth Authentication

To allow AI applications and clients to securely authenticate on behalf of users against the Looker-Managed MCP Server (`https://<YOUR_LOOKER_INSTANCE_URL>/mcp`), register your client application as an OAuth client in Looker.

### Step 1: Register OAuth Client Application

#### Option A: Using the Looker API Explorer (Recommended)
1. Open Looker and navigate to **Applications > API Explorer** (`https://<YOUR_LOOKER_INSTANCE_URL>/extensions/marketplace_extension_api_explorer::api-explorer/`).
2. Search for `register_oauth_client_app` (`POST /oauth_client_apps/{client_guid}`).
3. Enter your `<CLIENT_GUID>` and populate the request body (`client_guid`, `display_name`, `redirect_uri`, `enabled: true`).
4. Click **Run Request**.

#### Option B: Using `curl`

```bash
curl -X POST "https://<YOUR_LOOKER_INSTANCE_URL>/api/4.0/oauth_client_apps/<CLIENT_GUID>" \
  -H "Authorization: Bearer <ADMIN_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "client_guid": "<CLIENT_GUID>",
    "display_name": "My AI Assistant Client",
    "redirect_uri": "http://127.0.0.1:7777/oauth/callback",
    "enabled": true
  }'
```

- **`<CLIENT_GUID>`**: Unique client identifier for your integration (used as `clientId` in your MCP client's OAuth config).
- **`redirect_uri`**: Callback URL where authorization codes are sent:
  - **Antigravity**: `https://antigravity.google/oauth-callback`
  - **Claude Desktop / Claude AI**: `https://claude.ai/api/mcp/oauth/callback` or `http://localhost:<PORT>/oauth/callback`
  - **VS Code / Cloud Code**: `https://vscode.dev/redirect` or `http://127.0.0.1:<PORT>/oauth/callback`
  - **Cursor Desktop**: `https://cursor.com/mcp/callback`
  - **Generic CLI / Local Tools**: `http://127.0.0.1:7777/oauth/callback` or `http://localhost:8080/callback`

### Step 2: Perform OAuth PKCE Flow / Bearer Authentication

1. **Redirect User to Authorization URL:**
   Generate a PKCE `code_verifier` and SHA-256 `code_challenge`, then redirect the user to:
   ```text
   https://<YOUR_LOOKER_INSTANCE_URL>/auth/oauth?client_id=<CLIENT_GUID>&response_type=code&code_challenge=<PKCE_CHALLENGE>&code_challenge_method=S256&redirect_uri=<REDIRECT_URI>
   ```
2. **Exchange Authorization Code for Access & Refresh Tokens:**
   ```bash
   curl -X POST "https://<YOUR_LOOKER_INSTANCE_URL>/api/4.0/oauth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code" \
     -d "client_id=<CLIENT_GUID>" \
     -d "redirect_uri=<REDIRECT_URI>" \
     -d "code=<AUTHORIZATION_CODE>" \
     -d "code_verifier=<CODE_VERIFIER>"
   ```
3. **Authenticate MCP Requests:**
   Pass `Authorization: Bearer <ACCESS_TOKEN>` in HTTP headers sent to the MCP server.

---

## 2. Connecting MCP Clients (`mcp.json`)

### A. Remote / Looker-Managed MCP Configuration

#### Native OAuth Clients (e.g., Claude Desktop)
```json
{
  "mcpServers": {
    "Looker": {
      "httpUrl": "https://<YOUR_LOOKER_INSTANCE_URL>/mcp"
    }
  }
}
```

#### Standard HTTP Clients (Bearer Token via Headers)
```json
{
  "mcpServers": {
    "Looker": {
      "httpUrl": "https://<YOUR_LOOKER_INSTANCE_URL>/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_OAUTH_ACCESS_TOKEN>"
      }
    }
  }
}
```

### B. Local / Standalone MCP Toolbox Configuration

#### Stdio Mode (via `npx`)
```json
{
  "mcpServers": {
    "Looker": {
      "command": "npx",
      "args": ["-y", "@google/mcp-toolbox", "--prebuilt=looker,looker-dev"],
      "env": {
        "LOOKER_BASE_URL": "https://<YOUR_LOOKER_INSTANCE_URL>",
        "LOOKER_CLIENT_ID": "<YOUR_CLIENT_ID>",
        "LOOKER_CLIENT_SECRET": "<YOUR_CLIENT_SECRET>"
      }
    }
  }
}
```

#### HTTP Mode (via Docker Container)
Launch the container:
```bash
docker run -p 5000:5000 \
  -e LOOKER_BASE_URL="https://your-instance.looker.com" \
  -e LOOKER_CLIENT_ID="<CLIENT_ID>" \
  -e LOOKER_CLIENT_SECRET="<CLIENT_SECRET>" \
  us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest --prebuilt=looker,looker-dev --address=0.0.0.0
```

Then connect your MCP client to `http://localhost:5000/mcp`:
```json
{
  "mcpServers": {
    "Looker": {
      "httpUrl": "http://localhost:5000/mcp"
    }
  }
}
```
