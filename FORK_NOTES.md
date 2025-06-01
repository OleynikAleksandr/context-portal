# Notes on this Fork (OleynikAleksandr/context-portal)

This repository is a fork of the original [GreatScottyMac/context-portal](https://github.com/GreatScottyMac/context-portal) project, based on its `0.2.4` version.
The version of this fork is `0.2.4+fork.alembic_fixes` (see [`pyproject.toml`](pyproject.toml:7)).

The main purpose of this fork is to address issues encountered during the initial setup and launch of the ConPort MCP server, particularly in new or clean workspaces, related to the original 0.2.4 version.

## Key Fixes and Improvements:

1.  **Automatic Alembic Initialization:**
    *   Resolved an issue where Alembic configuration files (`alembic.ini`, `env.py`, and directory structure) were not automatically created on the first server run in a new workspace.
    *   The `ensure_alembic_files_exist` function was added to `src/context_portal_mcp/db/database.py` to copy necessary Alembic templates from `src/context_portal_mcp/templates/alembic/` to the active workspace's `context_portal` directory.
    *   Missing Alembic template files were created and added to the repository.
    *   *Files affected: `src/context_portal_mcp/db/database.py`, `src/context_portal_mcp/main.py` (import), new files in `src/context_portal_mcp/templates/alembic/`.*

2.  **`.gitignore` Correction:**
    *   Adjusted the [`.gitignore`](.gitignore) file to prevent it from ignoring the required Alembic template files within the `src/context_portal_mcp/templates/alembic/` directory.
    *   *Files affected: [`.gitignore`](.gitignore).*

3.  **Import Correction:**
    *   Fixed a `NameError` in `src/context_portal_mcp/main.py` related to the missing import of the `ensure_alembic_files_exist` function.
    *   *Files affected: `src/context_portal_mcp/main.py`.*

4.  **Dependency Installation Stability:**
    *   Checks were performed and potential issues with installing dependencies (including `alembic`) via `requirements.txt` in a virtual environment were addressed (though primarily through ensuring correct environment setup).
    *   *Files affected: (Primarily process, `requirements.txt` was confirmed to be okay).*

5.  **`README.md` Update:**
    *   Clarifications were added to [`README.md`](README.md:1) regarding instructions for manually running the server after installing from the Git repository.
    *   *Files affected: [`README.md`](README.md:1).*

6.  **Version Update in `pyproject.toml`:**
    *   The project version in [`pyproject.toml`](pyproject.toml:7) was updated to `0.2.4+fork.alembic_fixes` to reflect the forked and patched status.
    *   *Files affected: [`pyproject.toml`](pyproject.toml:7).*

These changes aim to ensure that ConPort MCP works correctly "out-of-the-box" immediately after cloning this fork and installing dependencies according to the instructions in [`README.md`](README.md:1). For detailed code changes, please refer to the Git commit history of this fork.