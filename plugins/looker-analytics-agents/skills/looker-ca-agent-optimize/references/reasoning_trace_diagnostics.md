# CA Agent Reasoning-Trace Diagnostics & Failure Patterns

During **Step 4 (`Optimize` Mode)**, inspect the Conversational Analytics (CA) response traces (`thoughts`, generated Looker queries, and tool invocation logs) for every failing or high-latency question in the Eval Suite. Classify each failure into one or more of the four canonical root causes below and apply the corresponding targeted fix.

---

## 1. Thought Loops / Multi-Query Stacking

### Symptoms in Reasoning Trace
- The CA Agent executes 3 to 6+ sequential Looker queries for a single user question instead of retrieving the answer in one consolidated query.
- The agent runs separate discovery queries to check dimension cardinalities or measure availability before running the final aggregation.
- High P50 / P90 latency (`> 25s`) and elevated token consumption even when the final answer is accurate.

### Root Cause
- System instructions lack explicit Explore-to-topic routing or fail to instruct the model to combine required dimensions and measures into a single query.
- The agent is unsure which measure represents the requested KPI and queries multiple candidate measures sequentially.

### Targeted Fixes (Cheapest-First)
1. **System Instructions (`<semantic_and_execution_rules>`):** Add a strict single-query consolidation rule:
   ```xml
   <semantic_and_execution_rules>
     - Execute a single consolidated Looker query containing all requested dimensions, measures, and filters whenever possible. Do not run preliminary exploratory queries to test field existence.
   </semantic_and_execution_rules>
   ```
2. **Golden Queries (`looker_golden_queries`):** Add 1–2 verified multi-field Golden Queries demonstrating how to combine the target dimensions, measures, and sorts in a single `looker_query` payload.

---

## 2. Field-Sampling Loops

### Symptoms in Reasoning Trace
- The CA Agent repeatedly calls `get_field_sample_values` / `get_field_value_suggestions` or runs `SELECT DISTINCT` Looker queries on categorical dimensions to map a user's natural language term (e.g., `"Enterprise"`, `"APAC"`, `"Paid"`, `"CA"`) to an exact database string.

### Root Cause
- Cryptic or non-obvious categorical values in the database (`"ENT_TIER_1"`, `"Y"/"N"`, `"1"/"0"`, state codes vs. full state names) are not documented in either the LookML field `description:` or the CA Agent's `<explore_and_filtering_rules>`.

### Targeted Fixes (Cheapest-First)
1. **System Instructions (`<explore_and_filtering_rules>`):** Inline the exact canonical filter value mappings for high-frequency dimensions:
   ```xml
   <explore_and_filtering_rules>
     - For `customers.segment`, map user terms directly to exact values: "Enterprise" -> "ENT_1", "Mid-Market" -> "MM_2", "SMB" -> "SMB_3". Do not sample field values for `customers.segment`.
   </explore_and_filtering_rules>
   ```
2. **LookML Metadata (`description:`):** Enrich the dimension's `description:` in the `.view.lkml` file with the allowed categorical values (for example: `description: "Customer tier. Valid values: ENT_1 (Enterprise), MM_2 (Mid-Market), SMB_3 (SMB)."`).

---

## 3. Data-Hunting Loops

### Symptoms in Reasoning Trace
- The user asks an undated or entity-specific question (e.g., `"What is the total revenue for Acme Corp?"`), and the CA Agent guesses an unrequested narrow date filter (such as `"last 7 days"` or `"current month"`) that returns `0 rows`.
- Upon receiving `0 rows`, the agent enters a panic retry loop, widening or shifting date filters across 3–5 consecutive queries until it finds rows or times out.

### Root Cause
- Overly rigid or ambiguous default date filter rules in `<explore_and_filtering_rules>` that force a narrow time window onto entity lookup queries, or missing guidance on how to handle undated queries.

### Targeted Fixes (Cheapest-First)
1. **System Instructions (`<explore_and_filtering_rules>`):** Clearly separate aggregate trend defaults from specific entity lookups:
   ```xml
   <explore_and_filtering_rules>
     - Apply the default filter `orders.created_date: "last 90 days"` ONLY for general trend or top-N summary questions when no date is specified.
     - Do NOT apply a default date filter when the user asks for lifetime totals or filters by a specific customer, order ID, or account name.
   </explore_and_filtering_rules>
   ```

---

## 4. Semantic & Filter Ambiguity

### Symptoms in Reasoning Trace
- The CA Agent completes in 1 query with low latency, but the returned numbers do not match Ground Truth because it selected the wrong LookML measure, wrong date dimension group (`created_date` vs. `shipped_date`), or omitted a mandatory business filter (such as `status: "Complete"` or `is_test_account: "No"`).

### Root Cause
- Multiple fields in the Explore have overlapping names without disambiguating `description:` parameters in LookML, or core business definitions are missing from `<semantic_and_execution_rules>`.

### Targeted Fixes (Cheapest-First)
1. **System Instructions (`<semantic_and_execution_rules>`):** Explicitly bind business terms to canonical `view.field` names and mandatory status filters.
2. **LookML Noise Reduction (`hidden: yes`):** Hide deprecated or duplicate measures/dimensions in `.view.lkml` (`hidden: yes`) and add explicit `description:` and `label:` tags to the canonical fields.
