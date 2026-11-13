# Step 1: System & IAM Pre-flight Checks (`onboarding-preflight-check`)

Verifies that the local environment has the required tools (`gcloud`, `bq`), active authentication, and directory write permissions before starting onboarding, and validates Looker Service Account IAM roles during Step 5 (BigQuery Connection).

## 1. Run the System Pre-flight Check

Execute the bundled pre-flight check script in `system` mode, specifying the directory where `looker-cli` is or will be installed (typically `~/.local/bin` or `./bin`):

```bash
scripts/preflight_check.sh \
  --mode system \
  --install-dir ~/.local/bin
```

---

## 2. Resolve System Check Failures

If the script exits with a non-zero status code, resolve the reported issue before advancing to Step 2:

### Case A: `gcloud CLI is not installed`
Install the Google Cloud SDK, or instruct the user to install it if system package manager permissions are restricted.

### Case B: `gcloud is not authenticated`
1. Prompt the user to authenticate interactively in their terminal:
   ```bash
   gcloud auth login
   ```
2. Wait for the user to finish authenticating, then re-run the `system` check.

### Case C: `bq CLI is not installed`
Install the BigQuery CLI component:
```bash
gcloud components install bq
```

### Case D: `Installation directory ... is not writable`
Create the directory if missing, or fall back to a writable workspace subdirectory (such as `./bin`) and pass that path to `--install-dir`.

---

## 3. Run the IAM Pre-flight Check (Used in Step 5: BigQuery Connection)

Before registering the BigQuery connection in Step 5, run the pre-flight script in `iam` mode to verify that the Looker Core service account holds the required least-privilege roles on the target BigQuery GCP project (`roles/bigquery.dataViewer`, `roles/bigquery.jobUser`, and `roles/serviceusage.serviceUsageConsumer`):

```bash
scripts/preflight_check.sh \
  --mode iam \
  --looker-project {looker_gcp_project_id} \
  --bq-project {bigquery_gcp_project_id}
```

> **Why `roles/serviceusage.serviceUsageConsumer` is required:** Google Cloud requires the Looker service account (`service-{project_number}@gcp-sa-looker.iam.gserviceaccount.com`) to have `serviceusage.services.use` permission in the billed project to dispatch BigQuery query jobs. Without it, queries fail with `400 Bad Request`.

If missing roles are reported, grant `roles/bigquery.dataViewer`, `roles/bigquery.jobUser`, and `roles/serviceusage.serviceUsageConsumer` using `gcloud projects add-iam-policy-binding` as detailed in [connecting-looker-to-bigquery.md](connecting-looker-to-bigquery.md).
