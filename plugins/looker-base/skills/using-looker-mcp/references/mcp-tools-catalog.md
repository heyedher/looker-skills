# Looker MCP Server Tools Catalog (45 Tools)

The Looker MCP Server exposes 45 tools organized across 6 functional categories.

## 1. Data & Query Execution

| Tool | Description |
| :--- | :--- |
| `query` | Executes structured queries using LookML model, explore, dimensions, measures, filters, sorts, and limits. |
| `query_sql` | Generates the underlying SQL query compiled by Looker for a given query definition. |
| `query_url` | Runs or resolves queries given a Looker shareable query URL or slug. |
| `run_look` | Executes a saved Look by ID and returns dataset results. |
| `run_dashboard` | Runs and executes element queries for a specified Dashboard ID. |

## 2. Discovery & Metadata Catalog

| Tool | Description |
| :--- | :--- |
| `get_models` | Lists all available LookML models in the instance. |
| `get_explores` | Lists Explores defined within a LookML model. |
| `get_dimensions` | Retrieves dimension fields defined for an Explore. |
| `get_measures` | Retrieves measure fields defined for an Explore. |
| `get_filters` | Retrieves filter-only fields defined for an Explore. |
| `get_parameters` | Retrieves parameters defined for an Explore. |
| `get_connections` | Lists database connection configurations. |
| `get_connection_databases` | Lists databases accessible via a connection. |
| `get_connection_schemas` | Lists schemas inside a database connection. |
| `get_connection_tables` | Lists database tables inside a connection schema. |
| `get_connection_table_columns` | Lists columns and metadata for a database table. |

## 3. Dashboards & Content Creation

| Tool | Description |
| :--- | :--- |
| `get_looks` | Searches and retrieves saved Looks. |
| `get_dashboards` | Searches and retrieves user-defined and LookML dashboards. |
| `make_look` | Creates a new saved Look from a query definition. |
| `make_dashboard` | Creates a new dashboard container. |
| `add_dashboard_element` | Adds visualization/data elements to a dashboard. |
| `add_dashboard_filter` | Adds dynamic interactive filters to a dashboard. |
| `generate_embed_url` | Generates signed SSO embed URLs for embedding Looker content. |

## 4. LookML Project Development

| Tool | Description |
| :--- | :--- |
| `dev_mode` | Toggles Development Mode vs Production Mode for the API session. |
| `get_projects` | Lists all LookML projects accessible to the session. |
| `get_project_directories` | Gets the directory structure tree of a project. |
| `get_project_files` | Lists files in a LookML project. |
| `get_project_file` | Views line contents of a specific LookML file. |
| `create_project_file` | Creates a new LookML file (`.lkml`, `.md`, etc.). |
| `update_project_file` | Updates line content of an existing LookML file. |
| `delete_project_file` | Removes a LookML file from the project workspace. |
| `create_project_directory` | Creates a subdirectory in the LookML project. |
| `delete_project_directory` | Deletes a project subdirectory. |
| `create_view_from_table` | Auto-generates standard LookML view definitions from a database table. |
| `validate_project` | Runs the LookML validator and returns compilation errors/warnings. |
| `get_lookml_tests` | Retrieves data test definitions written in LookML. |
| `run_lookml_tests` | Executes LookML data tests and returns pass/fail status. |

## 5. Git Version Control

| Tool | Description |
| :--- | :--- |
| `get_git_branch` | Retrieves active Git branch status for a LookML project. |
| `list_git_branches` | Lists remote and local Git branches. |
| `create_git_branch` | Creates a new Git working branch. |
| `switch_git_branch` | Switches project session context to specified Git branch. |
| `delete_git_branch` | Deletes a specified Git branch. |

## 6. Developer & Diagnostics Utilities

| Tool | Description |
| :--- | :--- |
| `health_pulse` | Performs lightweight liveness and health checks on the Looker instance. |
| `health_analyze` | Audits instance query performance and flags slow queries/PDT bottlenecks. |
| `health_vacuum` | Identifies un-utilized content, unused Explores, and candidate objects for cleanup. |
