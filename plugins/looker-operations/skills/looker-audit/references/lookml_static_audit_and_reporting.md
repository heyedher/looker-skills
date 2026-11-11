# Remote LookML Static Audit & Reporting Standards (`looker-audit`)

Procedures for remote LookML static anti-pattern scanning, unused model/field identification, and structured audit report generation.

---

## 1. Remote LookML Code Quality & Anti-Patterns

### Prioritization & 50-View Scaling Guardrail
1. **Identify Top Models by Query Volume:**
   ```bash
   echo '{"model":"system__activity","view":"history","fields":["query.model","history.query_run_count"],"sorts":["history.query_run_count desc"],"limit":"10"}' | looker-cli api query run_inline_query json - | jq
   ```
2. **Map Models to Projects:** Run `looker-cli api lookmlmodel all_lookml_models` to map high-usage models to project names. Focus static inspection on the top 3 projects.
3. **50-View Scaling Guardrail (Mandatory):** Before iterating over project files, count view files:
   ```bash
   looker-cli api project all_project_files "[PROJECT_ID]" | jq '[.[] | select(.type=="view")] | length'
   ```
   If the view count exceeds **50**, **pause and ask the user** which projects or files to prioritize before running exhaustive loops.

### Optimized Single-Pass Inspection Loop
To minimize API requests, run Looker's built-in validator and execute a single combined loop per project over `.lkml` files:

```bash
proj="[PROJECT_ID]"
echo "=== Auditing Remote LookML for Project: $proj ==="

# 1. Run built-in Looker validator
looker-cli api project validate_project "$proj" | jq

# 2. Single-pass inspection over all LKML files (with line numbers)
for file in $(looker-cli api project all_project_files "$proj" | jq -r '.[] | select(.extension==".lkml") | .path'); do
  content=$(looker-cli project file cat "$proj" "$file")

  # Wildcard Includes (Model files)
  echo "$content" | grep -n -iE 'include:\s*"*\*\.view' && echo "  [WARN] Wildcard include in $file"

  # Missing Primary Keys (View files)
  if [[ "$file" == *.view.lkml ]]; then
    echo "$content" | grep -q "primary_key:\s*yes" || echo "  [WARN] Missing primary key in $file"
  fi

  # Number Type for ID Dimensions
  echo "$content" | grep -n -iE "dimension:\s*[a-zA-Z0-9_]*id" -A 5 | grep -i "type:\s*number" && echo "  [WARN] Number ID dimension in $file"

  # Hardcoded Database References
  echo "$content" | grep -n 'sql:' | grep -v '\${' | grep '\.' && echo "  [WARN] Hardcoded DB ref in $file"
done
```

---

## 2. Unused LookML Projects, Views & Fields

### Unused LookML Projects (0 Queries in 365 Days)
Flag models/projects with **0 queries in 365 days** as primary candidates for archiving or deletion (excluding `system__activity` and active `marketplace_*` extension models):

```bash
echo '{"model":"system__activity","view":"history","fields":["query.model","history.query_run_count","history.most_recent_query_date"],"filters":{"history.created_date":"365 days"},"sorts":["history.query_run_count asc"],"limit":"500"}' | looker-cli api query run_inline_query json - | jq
looker-cli api lookmlmodel all_lookml_models | jq -r '.[] | {model: .name, project: .project_name}'
```

### Unused Fields & Views (0 Usage Across Explores in Last 90 Days)
```bash
echo '{"model":"system__activity","view":"field_usage","fields":["field_usage.explore","field_usage.view","field_usage.field","field_usage.times_used"],"filters":{"field_usage.times_used":"0"},"limit":"50"}' | looker-cli api query run_inline_query json - | jq
```

---

## 3. Audit Report Naming, Structure & Actionability Standards

- **Report File Naming Rule:** Name the report artifact `audit_report_[instance_name]_[timestamp].md` (e.g., `audit_report_gcpl264_202607091530.md`), sanitizing special characters and replacing spaces with underscores (`_`).
- **Required Header Metadata:**
  - **Timestamp:** Exact date and time of the audit (e.g., `2026-07-09 5:30PM`).
  - **Looker Instance:** Full URL of the audited Looker instance.
  - **Auditor:** AI agent/tool and model name used.
- **Severity & Priority Tiers:**
  - **High Priority:** Immediate impact on stability or performance (failing PDTs, systemic query errors, dashboard latency > 30s, broken datagroups).
  - **Medium Priority:** Moderate risk or performance drag (slow Explores 10–30s, tile bloat > 25 tiles, dynamic field abuse, merged queries, orphaned schedules).
  - **Low Priority:** Governance and cleanup hygiene (inactive accounts, unused content, `test`/`copy`/`draft` dashboards and Looks, non-critical schedule hotspots).
- **Exact Quantification & Concrete Examples:** Never use vague terms like "many" or "several". State exact counts (e.g., `"42 inactive accounts, including John Doe"` or `"Hotspot at 08:00 AM with 150 scheduled jobs"`).
- **Mandatory Actionability:** Accompany every finding with at least one of:
  1. A concrete **LookML code snippet** showing the fix (e.g., adding `primary_key: yes` to dimension `id` in view `orders`).
  2. The exact **`looker-cli` command** or inline JSON query to reproduce the full list.
  3. Exact **System Activity Explore** fields/filters and direct URL.
- **Direct Looker UI Hyperlinks:** Construct clickable links for every referenced asset:
  - **User-Defined Dashboard (UDD):** `https://[instance-url]/dashboards/[dashboard_id]`
  - **LookML Dashboard:** `https://[instance-url]/dashboards/[model_name]::[dashboard_name]`
  - **LookML IDE File & Line:** `https://[instance-url]/projects/[project_id]/files/[file_path]#L[line_number]`
  - **System Activity Explore:** `https://[instance-url]/explore/system__activity/[view_name]`
