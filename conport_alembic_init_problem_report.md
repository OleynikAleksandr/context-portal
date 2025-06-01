# Possible Problem with Alembic Initialization in New Workspace

When initializing ConPort MCP in a new project workspace, there may be issues if the workspace does not contain an `alembic` migration folder and an `alembic.ini` configuration file.

## Summary

- ConPort expects certain Alembic migration infrastructure to be present in the workspace (or a default location).
- If `alembic/` migration scripts and/or `alembic.ini` are missing, attempts to run migrations or initialize the database schema may result in errors or incomplete setup.
- This can cause the MCP server to start with errors, or fail to upgrade/initialize the schema correctly for the project.

## Typical Error Scenario

- After setting up a new workspace and launching ConPort MCP, the server may log errors about missing Alembic files or fail to apply database migrations.
- You might see messages like:  
  *"Can't locate alembic.ini"*,  
  *"No such file or directory: 'alembic'"*,  
  or similar errors related to migration scripts.

## Recommendation

- Always ensure that the required Alembic migration folder and `alembic.ini` exist in the workspace before initializing ConPort MCP.
- If they are missing, create them using `alembic init` and configure `alembic.ini` for the project database.
- Alternatively, check project documentation or ask the maintainer if migration infrastructure is set up differently.

---

*You can use this report as a context note when starting work in a fresh project to test and diagnose ConPort's behavior regarding Alembic migration files.*
