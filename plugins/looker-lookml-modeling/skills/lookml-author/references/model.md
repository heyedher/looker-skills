# LookML Models & Caching (`*.model.lkml`)

A LookML model file (`*.model.lkml`) binds a database connection, defines caching policies (`datagroup`), and includes the project's Explores, views, and dashboards.

## 1. Required Parameters & Core Settings

- **`connection: "connection_name"`**: Must match an active database connection configured in Looker Admin.
- **`label: "Friendly Name"`**: Provides a clean display name for the model in the Looker UI.
- **`week_start_day: monday`**: Optional; aligns date-week truncations with business reporting calendars.
- **`include: "pattern"`**: Controls which Explore, view, test, and dashboard files are scoped into the model.

---

## 2. Include Patterns & Scope Hygiene

Use strict, targeted `include` patterns to prevent namespace collisions and keep model compilation fast:

| Pattern | Description | Recommendation |
| :--- | :--- | :--- |
| `include: "/explores/orders.explore.lkml"` | Includes a dedicated Explore file | **Best Practice** (One Explore Per File pattern) |
| `include: "/views/marketing/users.view.lkml"` | Specific view file | **Best Practice** (Explicit, zero collision risk) |
| `include: "/views/marketing/*.view.lkml"` | All views in a domain folder | **Good** for domain-scoped modularity |
| `include: "/dashboards/*.dashboard.lookml"` | All LookML dashboards in folder | Standard for bundling LookML dashboards |
| `include: "/**/*.view.lkml"` | Recursive wildcard across entire repo | **Avoid** unless project is very small |

---

## 3. Datagroups & Caching Policies

Always prefer **Datagroups** over static `persist_for` timers to synchronize Looker's query cache and PDT rebuilds with upstream ETL/ELT completion.

- **`sql_trigger`**: A fast SQL query returning a single scalar value (e.g., `SELECT MAX(etl_loaded_at) ...`). When the returned value changes, Looker invalidates the cache and triggers dependent PDT rebuilds.
- **`max_cache_age`**: Fallback expiration threshold (e.g., `"24 hours"`) if the trigger value has not changed.
- **`persist_with`**: Applies the datagroup as the default caching policy at the model or Explore level.

### Datagroups vs. `persist_for`

| Feature | Datagroups (Recommended) | `persist_for` |
| :--- | :--- | :--- |
| **Invalidation Trigger** | SQL Query (`sql_trigger`) | Fixed duration timer |
| **Warehouse Alignment** | Synchronized with ETL/ELT completion | Unaligned (can serve stale data or expire early) |
| **Governance** | Centralized in `.model.lkml` | Scattered across Explores |
| **Appropriate Use Case** | Production models, dashboards, and PDTs | Real-time operational Explores (`persist_for: "5 minutes"`) |

---

## 4. Examples

### Production Model with Datagroup & Targeted Includes

```lookml
connection: "bigquery_analytics_prod"
label: "eCommerce Analytics"
week_start_day: monday

# Define ETL-aligned caching policy
datagroup: ecommerce_etl {
  description: "Triggers when a new batch is loaded into the events table."
  sql_trigger: SELECT MAX(DATE(created_at)) FROM `project.dataset.events` ;;
  max_cache_age: "24 hours"
}

# Apply default caching policy to all Explores in this model
persist_with: ecommerce_etl

# Include modular Explore files and LookML tests
include: "/explores/orders.explore.lkml"
include: "/explores/events.explore.lkml"
include: "/tests/*.test.lkml"
include: "/dashboards/*.dashboard.lookml"
```

### Self-Contained Model with Inline Explore & Real-Time Override

```lookml
connection: "thelook"

datagroup: daily_refresh {
  sql_trigger: SELECT CURRENT_DATE() ;;
  max_cache_age: "24 hours"
}

persist_with: daily_refresh

include: "/views/orders.view.lkml"
include: "/views/users.view.lkml"

explore: orders {
  label: "Orders"
  description: "Historical order analysis synchronized with daily ETL."
  join: users {
    type: left_outer
    relationship: many_to_one
    sql_on: ${orders.user_id} = ${users.id} ;;
  }
}

explore: live_order_queue {
  from: orders
  label: "Live Order Queue"
  description: "Near-real-time operational order feed."
  persist_for: "5 minutes"
}
```
