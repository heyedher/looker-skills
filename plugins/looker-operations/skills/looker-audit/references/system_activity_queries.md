# System Activity & Health Pulse Audit Queries (`looker-audit`)

Canonical `looker-cli health pulse` and `system__activity` inline JSON queries for auditing Looker instance health, dashboards, queries, PDTs, caching, users, content, and schedules.

> **Avoid Limit Truncation (Critical):** Always run the paired `count` query (or pipe IDs to `jq 'length'`) to report the exact total count of affected items rather than reporting a truncated `--limit` row count. Always pipe inline JSON via `echo '...' | looker-cli api query run_inline_query json -` and use SQL `%` wildcards instead of `*`.

---

## 1. High-Level Health Pulse Commands (7-Day Overview)

Run these commands first for a fast initial assessment before drilling into custom System Activity queries:

```bash
looker-cli health pulse dashboard-performance
looker-cli health pulse dashboard-errors
looker-cli health pulse explore-performance
looker-cli health pulse schedule-failures
looker-cli health pulse db-connections
```

---

## 2. Dashboard & Look Health and Complexity

### Tile Bloat (Dashboards with > 25 Tiles)
```bash
# Total Count
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.id"],"filters":{"dashboard_element.count":">25"}}' | looker-cli api query run_inline_query json - | jq 'length'

# Details
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.id","dashboard.title","dashboard_element.count"],"filters":{"dashboard_element.count":">25"},"sorts":["dashboard_element.count desc"],"limit":"50"}' | looker-cli api query run_inline_query json - | jq
```

### Auto-Refresh Enabled Dashboards
```bash
# Total Count
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.count"],"filters":{"dashboard.refresh_interval_ordered":"NOT NULL","dashboard.moved_to_trash":"No"}}' | looker-cli api query run_inline_query json - | jq

# Details
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.title","dashboard.refresh_interval_ordered","user.name","dashboard.id","dashboard_element.count","dashboard_element.count_text","dashboard_element.total_query_tiles"],"filters":{"dashboard.refresh_interval_ordered":"NOT NULL","dashboard.moved_to_trash":"No"},"sorts":["dashboard.refresh_interval_ordered"],"limit":"100"}' | looker-cli api query run_inline_query json - | jq
```

### Dynamic Fields (Table Calculations & Custom Fields > 2 per Tile)
Do not scan LookML files for dynamic fields—they live on dashboard/tile definitions:
```bash
# Total Count of Dashboards
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.id"],"filters":{"query.count_of_dynamic_fields":">2"}}' | looker-cli api query run_inline_query json - | jq 'length'

# Details
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.id","dashboard.title","query.count_of_dynamic_fields"],"filters":{"query.count_of_dynamic_fields":">2"},"sorts":["query.count_of_dynamic_fields desc"],"limit":"50"}' | looker-cli api query run_inline_query json - | jq
```

### Merged Queries (Client-Side Post-Query Joins)
```bash
# Total Count of Dashboards
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.count"],"filters":{"result_maker.is_merge_query":"Yes","dashboard.moved_to_trash":"No"}}' | looker-cli api query run_inline_query json - | jq

# Details
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.id","dashboard.title","dashboard_element.id","result_maker.merge_query_id"],"filters":{"result_maker.is_merge_query":"Yes","dashboard.moved_to_trash":"No"},"limit":"50"}' | looker-cli api query run_inline_query json - | jq
```

### Dashboard Average Runtime (Top 10 Slowest Dashboards)
```bash
echo '{"model":"system__activity","view":"dashboard_performance","fields":["dashboard.title","dashboard_history_stats.avg_runtime"],"sorts":["dashboard_history_stats.avg_runtime desc"],"limit":"10"}' | looker-cli api query run_inline_query json - | jq
```

---

## 3. Query Performance, Pipeline & Cache Health

### Slow Queries (> 10s in Last 30 Days)
```bash
echo '{"model":"system__activity","view":"history","fields":["history.created_time","history.source","history.runtime","query.model","query.view","user.name"],"filters":{"history.runtime":">10","history.created_date":"30 days","history.source":"explore,dashboard,look"},"sorts":["history.runtime desc"],"limit":"50"}' | looker-cli api query run_inline_query json - | jq
```

### Failed Datagroups
Check operational status via API/System Activity first; only inspect LookML files after identifying failing datagroups:
```bash
looker-cli api datagroup all_datagroups | jq '.[] | select(.trigger_error != null) | {name: .name, model: .model_name, error: .trigger_error}'
echo '{"model":"system__activity","view":"datagroup","fields":["datagroup.name","datagroup.model_name","datagroup.trigger_error"],"filters":{"datagroup.trigger_error":"-NULL"}}' | looker-cli api query run_inline_query json - | jq
```

### Failed Persistent Derived Tables (PDTs in Last 24 Hours)
When failures are identified, fetch the view definition (`looker-cli project file cat [PROJECT] [PATH]`) and check for unscoped `FROM table_name` references (use `${view_name.SQL_TABLE_NAME}`), non-portable SQL functions, or broken `datagroup_trigger` names:
```bash
# Total Count & Details
echo '{"model":"system__activity","view":"pdt_event_log","fields":["pdt_event_log.count"],"filters":{"pdt_event_log.action":"%error%","pdt_event_log.created_date":"24 hours"}}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"pdt_event_log","fields":["pdt_event_log.view_name","pdt_event_log.model_name","pdt_event_log.action","pdt_event_log.error_reason","pdt_event_log.created_time"],"filters":{"pdt_event_log.action":"%error%","pdt_event_log.created_date":"24 hours"},"sorts":["pdt_event_log.created_time desc"]}' | looker-cli api query run_inline_query json - | jq
```

### Cache Efficiency (Cache Hits vs. Live Queries — Target > 50%)
```bash
echo '{"model":"system__activity","view":"history","fields":["history.result_source","history.query_run_count"],"pivots":["history.result_source"],"filters":{"history.result_source":"-NULL","history.created_date":"30 days"},"sorts":["history.result_source"],"limit":"50"}' | looker-cli api query run_inline_query json - | jq
```

---

## 4. User, Content & Schedule Hygiene

### Inactive User Accounts (No UI Login in 90 Days)
```bash
echo '{"model":"system__activity","view":"user","fields":["user.count"],"filters":{"user_facts.last_ui_login_date":"before 90 days ago","user.is_disabled":"No"}}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"user","fields":["user.created_date","user.id","user.name","user_facts.last_ui_login_credential_type","user_facts.last_ui_login_date","history.most_recent_query_date"],"filters":{"user_facts.last_ui_login_date":"before 90 days ago","user.is_disabled":"No"},"sorts":["user.created_date desc"],"limit":"50"}' | looker-cli api query run_inline_query json - | jq
```

### Inactive Content (Not Accessed in >= 60 Days; Flag Annual/Quarterly Reports)
```bash
echo '{"model":"system__activity","view":"content_usage","fields":["content_usage.content_count"],"filters":{"content_usage.days_since_last_accessed":">=60","content_usage.dashboard_deleted":"No","content_usage.look_deleted":"No"}}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"content_usage","fields":["content_usage.content_id","content_usage.content_title","content_usage.content_type","content_usage.api_total","content_usage.embed_total","content_usage.favorites_total","content_usage.other_total","content_usage.schedule_total"],"filters":{"content_usage.days_since_last_accessed":">=60","content_usage.dashboard_deleted":"No","content_usage.look_deleted":"No"},"limit":"100"}' | looker-cli api query run_inline_query json - | jq
```

### Draft / Test / Copy Content (Dashboards & Looks)
```bash
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.count"],"filters":{"dashboard.title":"%test%,%copy%,%draft%","dashboard.moved_to_trash":"No"}}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"dashboard","fields":["dashboard.id","dashboard.title"],"filters":{"dashboard.title":"%test%,%copy%,%draft%","dashboard.moved_to_trash":"No"},"limit":"50"}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"look","fields":["look.count"],"filters":{"look.title":"%test%,%copy%,%draft%","look.deleted_date":"NULL"}}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"look","fields":["look.id","look.title"],"filters":{"look.title":"%test%,%copy%,%draft%","look.deleted_date":"NULL"},"limit":"50"}' | looker-cli api query run_inline_query json - | jq
```

### Schedule Hotspots, Failing Schedules & Orphaned Schedules (Disabled Owners)
*(Also inspect `looker-cli api scheduledplan all_scheduled_plans` for crontab definitions).*
```bash
echo '{"model":"system__activity","view":"scheduled_plan","fields":["scheduled_job.created_hour_of_day","scheduled_job.count"],"sorts":["scheduled_job.count desc"],"limit":"24"}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"scheduled_plan","fields":["scheduled_job.count"],"filters":{"scheduled_job.status":"failure"}}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"scheduled_plan","fields":["scheduled_plan.id","scheduled_plan.name","scheduled_job.status","scheduled_job.status_detail"],"filters":{"scheduled_job.status":"failure"},"limit":"50"}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"scheduled_plan","fields":["scheduled_plan.count"],"filters":{"user.is_disabled":"Yes"}}' | looker-cli api query run_inline_query json - | jq
echo '{"model":"system__activity","view":"scheduled_plan","fields":["scheduled_plan.id","scheduled_plan.name","user.name"],"filters":{"user.is_disabled":"Yes"},"limit":"50"}' | looker-cli api query run_inline_query json - | jq
```
