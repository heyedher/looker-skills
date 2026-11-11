# LookML SQL Dialect Migration Skill Guide (`lookml-dialect-migration`)

An automated SQL dialect migration skill for LookML projects powered by `looker-cli`. It audits entire Looker projects or targeted LookML files for source-dialect SQL functions, operators, identifier quoting, and semi-structured data syntax (such as Snowflake SQL), and proposes production-ready target-dialect equivalents (such as BigQuery Standard SQL).

---

## Prerequisites

To use this skill, `looker-cli` (`looker-base`) must be installed and authenticated to your Looker instance:

1. **Installation**: Verify `looker-cli --help` succeeds in your system `PATH`.
2. **Authentication**: Authenticate using OAuth PKCE (`looker-cli session login --oauth`) or API credentials (`looker-cli user me`).

---

## How to Use

Invoke the skill by asking the agent to check or migrate your LookML SQL dialect (for example, Snowflake to BigQuery Standard SQL) across an entire project or a specific file on any existing branch.

### Required Inputs
- **Looker Instance URL** (e.g., `https://mycompany.looker.com` or Looker Core URL)
- **Project Name** (e.g., `my_analytics_project`)
- **Branch Name** (e.g., `master` or `main`)
- *(Optional)* **Target File** (e.g., `views/snowflake_orders.view.lkml`)

### Example Prompts
```text
"Check project 'my_analytics_project' in https://mycompany.looker.app on branch 'master' for Snowflake syntax and propose BigQuery equivalents."
"Migrate the view 'views/snowflake_orders.view.lkml' in 'my_analytics_project' on branch 'dev-branch' from Snowflake to BigQuery."
```

---

## Bundle Structure

```text
lookml-dialect-migration/
├── SKILL.md
└── references/
    ├── guide.md
    └── snowflake-to-bigquery.md
```
