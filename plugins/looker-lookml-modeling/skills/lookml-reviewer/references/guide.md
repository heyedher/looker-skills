# LookML Reviewer Skill Guide

An automated code review skill for LookML projects powered by `looker-cli`. It audits entire projects or targeted LookML files against official Looker best practices, LAMS style standards, and Conversational Analytics readiness.

---

## Prerequisites

To use this skill, `looker-cli` (`looker-base`) must be installed and authenticated to your Looker instance:

1. **Installation**: Verify `looker-cli --help` succeeds in your system `PATH`.
2. **Authentication**: Authenticate using OAuth PKCE (`looker-cli session login --oauth`) or API credentials (`looker-cli user me`).

---

## How to Use

Invoke the skill by asking the agent to review your LookML code. You can review an entire project or a specific file on any existing Git branch.

### Required Inputs
- **Looker Instance URL** (e.g., `https://mycompany.looker.com` or Looker Core URL)
- **Project Name** (e.g., `fashionly`)
- **Branch Name** (e.g., `master` or `main`)
- *(Optional)* **Target File** (e.g., `views/order_items.view.lkml`)

### Example Prompts
```text
"Review the LookML in project 'fashionly' on branch 'master' at https://mycompany.looker.app."
"Audit the view 'views/order_items.view.lkml' in the 'fashionly' project on branch 'dev-branch'."
```

---

## Bundle Structure

```text
lookml-reviewer/
├── SKILL.md
└── references/
    ├── guide.md
    ├── lookml-dos-and-donts.md
    ├── lams-style-guide.md
    ├── sustainable-maintainable-lookml.md
    └── conversational-analytics-best-practices.md
```
