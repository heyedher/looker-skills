# Step 7: Authoring LookML Views, Model & Verification Queries (`lookml-model-create`)

Guides you through authoring the LookML view files and model file for the user's onboarding dashboard goal, registering the model connection mapping, validating the project with zero errors, and running a verification query.

## Prerequisites & Style Standards

- `looker-cli` is authenticated and the BigQuery connection (`{connection_name}`) and Looker project (`{project_id}`) are configured (Steps 3–6).
- **Mandatory Style Reference:** Strictly enforce all naming, primary key, join, and documentation rules in [lookml-style-guide.md](lookml-style-guide.md).

---

## Instructions

### 1. Map Schema from Step 2 Discovery

Recall the exact specifications agreed upon with the user in Step 2 ([exploring-data-for-looker.md](exploring-data-for-looker.md)):
1. Target **Dashboard Goal** and required visual breakdowns.
2. Exact **GCP Project ID**, **Dataset ID**, and **Table Names** (fact and dimension tables).
3. Exact column names and data types from `bq show`—never guess column names.

---

### 2. Create & Upload LookML View Files (`views/*.view.lkml`)

1. Create the `views/` directory in the project if it does not yet exist:
   ```bash
   looker-cli session update dev && looker-cli project directory create {project_id} views
   ```
2. For each required BigQuery table, write `/tmp/{table_name}.view.lkml` following [lookml-style-guide.md](lookml-style-guide.md):
   - Set explicit ``sql_table_name: `{gcp_project_id}.{dataset_name}.{table_name}` ;;``.
   - Place the primary key dimension first with `primary_key: yes`.
   - Use `dimension_group` with `type: time` and `timeframes: [raw, time, date, week, month, quarter, year]` for timestamps (and `type: duration` for date diffs).
   - Reference dimensions (`${sale_price}`) rather than raw columns inside measures, and include `description:` on every field.
3. Upload each view file to the project:
   ```bash
   looker-cli project file create {project_id} views/{table_name}.view.lkml /tmp/{table_name}.view.lkml
   ```

---

### 3. Create & Upload the LookML Model File (`{model_name}.model.lkml`)

1. Write `/tmp/{model_name}.model.lkml`:
   - Set `connection: "{connection_name}"`.
   - Include each specific view file (`include: "/views/{table_name}.view.lkml"`—avoid recursive `/**/*.view.lkml` wildcards).
   - **Mandatory Dashboard Include:** Add `include: "/dashboards/*.dashboard.lookml"` so Step 8 dashboards are discovered by the validator and importer.
   - Define the `explore:` block with `description:`, `label:`, and explicit `relationship:` (`many_to_one`, `one_to_one`, etc.) and `sql_on:` on every `join:`.
2. Upload the model file to the project root:
   ```bash
   looker-cli project file create {project_id} {model_name}.model.lkml /tmp/{model_name}.model.lkml
   ```

---

### 4. Register the Model Connection Mapping in Looker (Mandatory)

1. Write `/tmp/model_config.json`:
   ```json
   {
     "name": "{model_name}",
     "project_name": "{project_id}",
     "allowed_db_connection_names": ["{connection_name}"]
   }
   ```
2. Import and verify the model configuration:
   ```bash
   looker-cli model import /tmp/model_config.json
   looker-cli model cat {model_name}
   ```
   Confirm `allowed_db_connection_names` includes `"{connection_name}"`.

---

### 5. Validate LookML & Run Verification Query

1. **Validate LookML (Zero-Error Policy):**
   ```bash
   looker-cli api project validate_project {project_id}
   ```
   If any errors are returned, update the local files, push via `looker-cli project file update`, and re-validate until zero errors remain.
2. **Execute an Inline Verification Query:**
   Write `/tmp/verify_query.json` requesting a dimension and measure from your Explore:
   ```json
   {
     "model": "{model_name}",
     "view": "{explore_name}",
     "fields": ["{view_name}.{dimension_name}", "{view_name}.{measure_name}"],
     "limit": 5
   }
   ```
   Run the query and verify that rows return without SQL errors:
   ```bash
   looker-cli query runquery --file /tmp/verify_query.json --format json
   ```
