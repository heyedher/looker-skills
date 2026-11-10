# Step 2: Onboarding Interview & BigQuery Data Discovery (`exploring-data-for-looker`)

Guides you through interviewing the user to understand their analytics goal and exploring their BigQuery dataset to propose an actionable first dashboard.

## Prerequisites

- System pre-flight check (Step 1) has passed (`gcloud` and `bq` installed and authenticated).
- The user has a Looker instance ready for onboarding.

---

## Instructions

### 1. Interview the User (Blocking Step)

Start by interviewing the user to capture their business goal and target GCP project/dataset. **Do not run any `gcloud` or `bq` commands before asking these questions and receiving the user's reply.**

Ask the user:

> "Welcome to Looker! To help you get started, I'll guide you through connecting your data, setting up a project, and building your first dashboard.
>
> To make sure we build something tailored to your needs, could you tell me:
> 1. What is the main goal of your Looker exploration? (e.g., Sales analysis, User behavior, Inventory tracking, Support metrics)
> 2. Which BigQuery GCP project ID and dataset contain the data you want to use?
> 3. Are there specific metrics (e.g., total revenue, active users) or dimensions (e.g., product category, region) you are most interested in?"

**STOP AND WAIT** for the user's response before calling any tools.

---

### 2. Explore BigQuery Data (`bq`)

Once the user provides the target GCP project and dataset, inspect the dataset structure using the `bq` CLI.

> **Important:** Do **not** assume table naming conventions such as `dim_` or `fct_` prefixes. Identify fact and dimension tables by inspecting their actual schemas (timestamps, numeric measures, primary/foreign keys).

1. **List Datasets in the GCP Project (if dataset wasn't specified):**
   ```bash
   bq ls --project_id={gcp_project_id}
   ```
2. **List Tables in the Target Dataset:**
   ```bash
   bq ls {gcp_project_id}:{dataset_name}
   ```
   - **Fact tables:** Transactional or event tables containing timestamps and numeric metrics (e.g., `orders`, `order_items`, `events`, `payments`).
   - **Dimension tables:** Entity lookup tables containing descriptive attributes (e.g., `users`, `products`, `customers`, `locations`).
3. **Inspect Table Schemas for Candidate Tables:**
   ```bash
   bq show --format=prettyjson {gcp_project_id}:{dataset_name}.{table_name}
   ```
   Record the exact column names, data types (`TIMESTAMP`, `DATE`, `INT64`, `FLOAT64`, `NUMERIC`, `STRING`), primary keys, and foreign keys for Step 7.

---

### 3. Propose the Onboarding Dashboard Goal

Based on the user's answers and the discovered schema, propose a concrete dashboard plan:

> "I've explored your dataset `{dataset_name}` and identified the key tables:
> - `{table_1}` (transactional data with timestamps and metrics)
> - `{table_2}` (entity dimensions for grouping and filtering)
>
> I propose we build a **{Dashboard Title}** featuring:
> 1. **{Metric 1}** over time (daily/monthly).
> 2. **Top {Dimension}** by **{Metric 2}**.
> 3. **{Dimension Breakdown}** distribution.
>
> Does this sound good? Once confirmed, we'll verify the Looker CLI and connect your BigQuery dataset!"
