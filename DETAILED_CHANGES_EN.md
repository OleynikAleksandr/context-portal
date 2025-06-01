# Detailed Change List for the ConPort Fork (OleynikAleksandr/context-portal)

## Goal: Automatic DB initialization with table creation

**Last updated:** 2025-06-01

---

### 1. Module `src.context_portal_mcp.db.database`

* **`ensure_alembic_files_exist(workspace_root_dir: Path)`:**
  * **Changed:** The logic for copying Alembic templates. Instead of merely copying `alembic.ini` and the `alembic/` directory (which could be empty or incomplete in the templates), the function now uses `shutil.copytree` to recursively copy the entire content of `src/context_portal_mcp/templates/alembic/alembic/` to `[workspace_root_dir]/alembic/`. This includes `env.py`, `script.py.mako`, and crucially the `versions/` subdirectory with all generated migration files.
  * Added a check and creation of the `versions` directory inside `[workspace_root_dir]/alembic/` if `copytree` did not create it.

* **`run_migrations(db_path: Path, project_root_dir: Path)`:**
  * **Changed:** Path configuration for Alembic `Config`.
    * `alembic_ini_path`: now uses `.resolve()` to obtain an absolute path.
    * `alembic_scripts_path`: now uses `.resolve()` and is passed to `cfg.set_main_option("script_location", str(alembic_scripts_path))`.
    * `sqlalchemy.url`: now formed using `db_path.resolve()` to ensure an absolute path: `sqlite:///{resolved_db_path}`.
  * **Added:** More detailed logging for debugging paths and Alembic configuration.
  * **Added:** Explicit check for `alembic.ini` and `alembic/versions` directory existence before calling `command.upgrade`.

---

### 2. Alembic Templates (`src.context_portal_mcp.templates.alembic`)

* **Base Alembic template structure created** as it was missing:
  * **`src/context_portal_mcp/templates/alembic/alembic.ini`:**
    * Standard `alembic.ini` created.
    * `script_location` set to `%(here)s/alembic` for correct path resolution after copying to the workspace.
    * `sqlalchemy.url` set to `sqlite:///./placeholder_conport.db` (overridden in `run_migrations`).
  * **`src/context_portal_mcp/templates/alembic/alembic/script.py.mako`:**
    * Standard `script.py.mako` created.
    * **Fixed:** The expression for `down_revision` changed from `${down_revision | PythonLiteral}` to `${repr(down_revision)}` for correct handling in the first migration where `down_revision` is `None`.
  * **`src/context_portal_mcp/templates/alembic/alembic/env.py`:**
    * Standard `env.py` created.
    * **Changed:** Modified path addition logic to `sys.path` for more robust discovery of the `src` package when running `alembic` from the command line. Now adds `GRANDPARENT_DIR` (parent of the project root) and `SRC_PARENT_DIR` (project root).
    * **Changed:** `target_metadata` is now imported from the new file `src.context_portal_mcp.db.orm_models`:
      ```python
      from src.context_portal_mcp.db.orm_models import Base
      target_metadata = Base.metadata
      ```
  * **`src/context_portal_mcp/templates/alembic/alembic/versions/`:**
    * Directory created (initially with `.gitkeep`, later overwritten).
    * **Migration file added:** After setup, the command
      ```bash
      python -m alembic -c src/context_portal_mcp/templates/alembic/alembic.ini revision -m "create_initial_conport_tables" --autogenerate
      ```
      generated the initial migration file (`b7798b697008_create_initial_conport_tables.py`), which is now part of the templates.

---

### 3. SQLAlchemy ORM Models (`src.context_portal_mcp.db.orm_models`)

* **New file `src/context_portal_mcp/db/orm_models.py` created:**
  * Contains the definition: `Base = declarative_base()`.
  * Added examples of ORM models (`ProductContextORM`, `ActiveContextORM`, `DecisionORM`) corresponding to database tables.
  * **Needs work:** ORM definitions for all other ConPort tables (ProgressEntry, SystemPattern, CustomData, ContextLink, history tables, etc.) must be added so Alembic autogeneration can include them.

---

### 4. Source File `src.context_portal_mcp.main` (fix for previous error)

* In the `except ImportError` fallback, added an import for `ensure_alembic_files_exist`:
  ```python
  from src.context_portal_mcp.db.database import ensure_alembic_files_exist
  ```
  This fixed the `NameError` when running the server in STDIO mode and using the fallback import path.

---

**General result:**
After these changes, provided that `src/context_portal_mcp/db/orm_models.py` includes complete definitions for all tables and the migration is regenerated to include them, ConPort should automatically create and set up the database with all tables on first run in a new workspace.

---

### 5. Additional Changes (2025-06-01)

| File/Component                          | Change |
|------------------------------------------|--------|
| `src.context_portal_mcp.db.database`     | • `_add_context_history_entry` — added **`context_id`** parameter and logic for column selection (`product_context_id` / `active_context_id`).<br>• `update_product_context` and `update_active_context` now pass `1` as `context_id`. |
| Initial migration script                 | The corrected `3d3360227021_create_initial_conport_tables_v2.py` includes:<br>• History tables `product_context_history`, `active_context_history` with columns `timestamp`, `version`, `change_source`, and references to the main tables.<br>• Insertion of initial rows into `product_context` and `active_context`. |
| Alembic templates                        | The directory `templates/alembic/alembic/versions/` contains the **only** correct migration file. |
| Repository cleanup                       | Removed root-level duplicate files (`3d3360227021_create_initial_conport_tables_v2.py`, `CONPORT_FULL_TEST_REPORT.md`). Commit `b15e58b`. |

> After these fixes, ConPort initializes the database in a clean workspace without errors and properly maintains context change history.