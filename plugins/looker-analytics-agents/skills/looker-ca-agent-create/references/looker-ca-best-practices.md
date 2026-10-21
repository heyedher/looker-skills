# Looker Conversational Analytics (CA) Best Practices

This shared reference defines the foundational grounding standards that all Looker Conversational Analytics (CA) skills (`looker-ca-agent-optimize` and `looker-ca-agent-create`) must enforce when auditing, authoring, or optimizing Standalone Agents and Dashboard Agents.

---

## 1. Four-Part System Instructions Structure (XML or YAML)

System instructions for a Looker CA Agent must never be written as unstructured plain-text paragraphs. Always structure system instructions into four explicit sections using XML tags or YAML keys, and keep total instructions concise to stay within the recommended token budget:

1. **Role & Tone (`<role_and_tone>`):**
   - Define a concise persona, target audience, and strict domain boundary (for example: "Act as a Retail Merchandising Analyst answering questions strictly from the `orders` and `inventory` Explores").
   - Prohibit fabricating metrics or extrapolating outside the attached Explores/Dashboard.

2. **Explore & Filtering Rules (`<explore_and_filtering_rules>`):**
   - Explicitly map question topics to the designated Explore when multiple Explores are attached.
   - Define mandatory default filters (such as default date ranges, active status flags, or excluded test accounts) and explicit exceptions when a user specifies a custom time window or cohort.
   - Inline common categorical filter value mappings (for example, mapping `"US"` / `"United States"` to `"USA"`) so the agent does not enter field-sampling loops.

3. **Semantic Layer & Execution Rules (`<semantic_and_execution_rules>`):**
   - Disambiguate closely named measures and dimensions (for example, specifying when to use `net_revenue` vs. `gross_margin`).
   - Map boolean and status phrases to exact LookML field values.
   - Enforce single-query consolidation: instruct the agent to retrieve required dimensions and measures in a single Looker query rather than stacking multiple exploratory queries.

4. **Presentation & Analysis Rules (`<presentation_and_analysis_rules>`):**
   - Specify default grouping dimensions, Top-N sorting rules, and number/currency formatting expectations.

### Canonical XML Template

```xml
<agent_instructions>
  <role_and_tone>
    Persona, domain scope, and response conciseness rules.
  </role_and_tone>
  <explore_and_filtering_rules>
    Primary Explore routing, mandatory default filters, date fallbacks, and inlined filter value mappings.
  </explore_and_filtering_rules>
  <semantic_and_execution_rules>
    Metric disambiguation rules, calculation guardrails, and single-query execution enforcement.
  </semantic_and_execution_rules>
  <presentation_and_analysis_rules>
    Default breakdown dimensions, Top-N limits, and sorting conventions.
  </presentation_and_analysis_rules>
</agent_instructions>
```

---

## 2. Explore Scoping Guardrails

- **Connect Only to Curated Explores:** Attach the CA Agent only to purpose-built, curated Explores required for its domain. Avoid attaching wide "mega-explores" with hundreds of uncurated joined views.
- **Avoid Duplicate Context:** Any context already defined in structured fields (`looker_golden_queries` or LookML `description:` parameters) is automatically injected into the agent prompt. Do not duplicate full field catalogs inside `system_instruction`.

---

## 3. Golden Query Curation Standards (`looker_golden_queries`)

Golden Queries apply to **Standalone Agents** and consist of verified `(natural_language_questions, looker_query)` pairs that teach the agent how to handle complex joins, cohorts, and filter patterns:

- **Quantity Cap (`< 20` Total):** Maintain between **3 and 15** high-value Golden Queries (strictly **fewer than 20**). Excessive golden queries inflate latency and token consumption.
- **Anti-Overfitting Rule:** Golden queries must represent reusable query archetypes (e.g., period-over-period comparisons, cohort filters, multi-view joins). Never overfit by generating exact golden queries for more than **50%** of an evaluation test suite's questions.
- **Required `looker_query` Schema Fields:**
  - `model` (required): Exact LookML model name.
  - `explore` (required): Exact LookML Explore name.
  - `fields` (required): List of fully qualified `view_name.field_name` strings.
  - `filters` (optional): Array of `{"field": "view.field", "value": "..."}` objects.
  - `sorts` (optional): Array of sort strings (e.g., `["view.measure desc"]`).

---

## 4. Delegate Reusable Logic to LookML

Whenever a business calculation, field alias, or join constraint applies across multiple agents or users, push that logic into the **LookML semantic layer** (via `description:`, `label:`, `sql:`, or `access_filter`) rather than hardcoding complex SQL/calculation formulas inside the CA Agent's system instructions.
