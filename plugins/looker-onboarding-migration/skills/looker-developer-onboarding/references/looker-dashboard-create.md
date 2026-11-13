# Step 8: Creating, Importing & Iterating on the Dashboard (`looker-dashboard-create`)

Guides you through the final onboarding step: authoring a LookML dashboard (`*.dashboard.lookml`), importing it as a User-Defined Dashboard (UDD) in the Shared folder, verifying every tile's SQL query, and iterating on user feedback.

## Prerequisites

- LookML views and model (`{model_name}.model.lkml`) are validated and verified via query (Step 7: [lookml-model-create.md](lookml-model-create.md)).
- `{model_name}.model.lkml` includes `/dashboards/*.dashboard.lookml` (or `/dashboards/**/*.dashboard.lookml`).

---

## Instructions

### 1. Identify the Target `"Shared"` Folder ID

Locate the ID of the default **Shared** folder on the Looker instance (typically `"1"` on a fresh instance):

```bash
looker-cli folder ls
```

Record the `id` of the `"Shared"` folder as `{folder_id}`.

---

### 2. Author & Upload the LookML Dashboard File

1. Create the `dashboards/` directory in the project:
   ```bash
   looker-cli session update dev && looker-cli project directory create {project_id} dashboards
   ```
2. Write `/tmp/{dashboard_name}.dashboard.lookml` using **`layout: newspaper`** (24-column grid with `row`, `col`, `width`, `height`) and fully qualified `view_name.field_name` references:
   ```yaml
   - dashboard: sales_performance
     title: Sales Performance Overview
     layout: newspaper
     preferred_viewer: dashboards-next

     elements:
       - name: total_revenue_tile
         title: Total Revenue Over Time
         model: ecommerce
         explore: orders
         type: looker_line
         fields: [orders.created_date, orders.total_revenue]
         sorts: [orders.created_date desc]
         limit: 500
         row: 0
         col: 0
         width: 12
         height: 8

       - name: top_categories_tile
         title: Top Categories by Order Count
         model: ecommerce
         explore: orders
         type: looker_column
         fields: [products.category, orders.count_orders]
         sorts: [orders.count_orders desc]
         limit: 10
         row: 0
         col: 12
         width: 12
         height: 8
   ```
3. Upload the dashboard file and validate the project:
   ```bash
   looker-cli project file create {project_id} dashboards/{dashboard_name}.dashboard.lookml /tmp/{dashboard_name}.dashboard.lookml
   looker-cli api project validate_project {project_id}
   ```

---

### 3. Import the LookML Dashboard as a UDD

Switch to the `dev` workspace and import the LookML dashboard (`{model_name}::{dashboard_name}`) into `{folder_id}`:

```bash
looker-cli session update dev && looker-cli dashboard import lookml {model_name}::{dashboard_name} {folder_id}
```

Record the numeric `{udd_id}` returned in the JSON response.

---

### 4. Verify Every Tile's SQL Query Execution (Mandatory)

LookML validation only checks syntax—it does not execute the underlying SQL for each tile. Before sharing the dashboard URL with the user, execute every tile query:

1. Fetch all `query_id` values on the imported UDD:
   ```bash
   looker-cli dashboard cat {udd_id} --fields "dashboard_elements(query_id)"
   ```
2. Execute each non-null `query_id`:
   ```bash
   looker-cli query runquery {query_id}
   ```
3. If any tile query fails, fix the underlying LookML view/dashboard file, re-run `validate_project`, synchronize via `looker-cli dashboard sync lookml {model_name}::{dashboard_name}`, and re-verify until every tile query succeeds.

---

### 5. Present Dashboard URL & Iterate with User

1. Share the live dashboard URL (`{instance_url}/dashboards/{udd_id}`) with the user and ask for feedback on chart types, metrics, filters, or layout. **Stop and wait** for the user's response.
2. When the user requests refinements:
   ```bash
   # 1. Update the LookML dashboard file
   looker-cli project file update {project_id} dashboards/{dashboard_name}.dashboard.lookml /tmp/{dashboard_name}.dashboard.lookml

   # 2. Validate LookML
   looker-cli api project validate_project {project_id}

   # 3. Sync changes to the imported UDD in dev mode
   looker-cli session update dev && looker-cli dashboard sync lookml {model_name}::{dashboard_name}
   ```
3. Re-run the tile query verification check (Section 4) and ask the user to refresh their browser until they are satisfied.
