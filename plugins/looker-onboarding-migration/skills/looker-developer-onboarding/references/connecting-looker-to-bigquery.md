# Step 5: Connecting Looker to BigQuery (`connecting-looker-to-bigquery`)

Creates a database connection in Looker to Google BigQuery using **Application Default Credentials (ADC)**—the recommended keyless authentication method for Looker Core instances on Google Cloud.

## Prerequisites

- `looker-cli` is installed and authenticated (Steps 3 & 4: [looker-cli-setup.md](looker-cli-setup.md) and [looker-cli-auth.md](looker-cli-auth.md)).
- Target BigQuery **GCP Project ID** (supports hyphens) and **Dataset ID** (alphanumeric/underscores only) were identified in Step 2 ([exploring-data-for-looker.md](exploring-data-for-looker.md)).

---

## Instructions

### 1. Verify Looker Service Account IAM Roles

Verify that the Looker Core service account (`service-{project_number}@gcp-sa-looker.iam.gserviceaccount.com`) has the three required IAM roles on the BigQuery GCP project (`roles/bigquery.dataViewer`, `roles/bigquery.jobUser`, and `roles/serviceusage.serviceUsageConsumer`):

1. Run the pre-flight check script in `iam` mode:
   ```bash
   scripts/preflight_check.sh \
     --mode iam \
     --looker-project {looker_gcp_project_id} \
     --bq-project {bigquery_gcp_project_id}
   ```
2. If any roles are missing, retrieve the Looker GCP project number and bind the required roles:
   ```bash
   project_number=$(gcloud projects describe {looker_gcp_project_id} --format="value(projectNumber)")

   gcloud projects add-iam-policy-binding {bigquery_gcp_project_id} \
     --member="serviceAccount:service-${project_number}@gcp-sa-looker.iam.gserviceaccount.com" \
     --role="roles/bigquery.dataViewer"

   gcloud projects add-iam-policy-binding {bigquery_gcp_project_id} \
     --member="serviceAccount:service-${project_number}@gcp-sa-looker.iam.gserviceaccount.com" \
     --role="roles/bigquery.jobUser"

   gcloud projects add-iam-policy-binding {bigquery_gcp_project_id} \
     --member="serviceAccount:service-${project_number}@gcp-sa-looker.iam.gserviceaccount.com" \
     --role="roles/serviceusage.serviceUsageConsumer"
   ```

---

### 2. Write the Connection Configuration Payload

Write the connection specification to `/tmp/connection_config.json`:

> **BigQuery JDBC Mapping Rule:**
> - **`host`** must be set to the **GCP Project ID** (supports hyphens).
> - **`database`** and **`schema`** must both be set to the **BigQuery Dataset ID** (alphanumeric and underscores only). Setting `database` to a hyphenated project ID causes query failures.

```json
{
  "name": "{connection_name}",
  "dialect_name": "bigquery_standard_sql",
  "uses_application_default_credentials": true,
  "host": "{gcp_project_id}",
  "database": "{dataset_name}",
  "schema": "{dataset_name}"
}
```

---

### 3. Import & Verify the Connection in Looker

1. Import the connection payload via `looker-cli`:
   ```bash
   looker-cli connection import /tmp/connection_config.json
   ```
2. Verify the connection was registered cleanly:
   ```bash
   looker-cli connection cat {connection_name}
   ```
