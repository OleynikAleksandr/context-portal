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
      generated the initial migration file (`b7798b697008_create_initial_conport_tables.py`), which is now part of the templates. This was later replaced by `3d3360227021_create_initial_conport_tables_v2.py`.
    * **New migration file added (2025-06-01):** `5cf9ea8bcc0b_add_custom_data_and_history_tables.py` was generated to include `CustomDataORM`, history tables, and other schema additions.

---

### 3. SQLAlchemy ORM Models (`src.context_portal_mcp.db.orm_models`)

* **File `src/context_portal_mcp/db/orm_models.py` updated:**
  * Contains the definition: `Base = declarative_base()`.
  * **Updated (2025-06-01):** The file was significantly updated to include ORM definitions for all core ConPort tables:
    * `ProductContextORM` (with `history` relationship)
    * `ActiveContextORM` (with `history` relationship)
    * `DecisionORM`
    * `ProgressEntryORM` (with parent/child relationships)
    * `SystemPatternORM` (with unique constraint on name)
    * `CustomDataORM` (with unique constraint on category/key)
    * `ProductContextHistoryORM` (with ForeignKey to `product_context` and `ondelete="CASCADE"`)
    * `ActiveContextHistoryORM` (with ForeignKey to `active_context` and `ondelete="CASCADE"`)
    * `ContextLinkORM`
    * Relationships between main context tables and their history tables were also defined.
    * Indexing was added to key columns for performance.

---

### 4. Source File `src.context_portal_mcp.main` (fix for previous error)

* In the `except ImportError` fallback, added an import for `ensure_alembic_files_exist`:
  ```python
  from src.context_portal_mcp.db.database import ensure_alembic_files_exist
  ```
  This fixed the `NameError` when running the server in STDIO mode and using the fallback import path.

---

**General result:**
After these changes, ConPort should automatically create and set up the database with all tables, including `custom_data` and related entities, on first run in a new workspace.

---

### 5. Additional Changes (Chronological)

| Date       | File/Component                          | Change |
|------------|------------------------------------------|--------|
| 2025-06-01 | `src.context_portal_mcp.db.database`     | • `_add_context_history_entry` — added **`context_id`** parameter and logic for column selection (`product_context_id` / `active_context_id`).<br>• `update_product_context` and `update_active_context` now pass `1` as `context_id`. |
| 2025-06-01 | Initial migration script                 | The corrected `3d3360227021_create_initial_conport_tables_v2.py` includes:<br>• History tables `product_context_history`, `active_context_history` with columns `timestamp`, `version`, `change_source`, and references to the main tables.<br>• Insertion of initial rows into `product_context` and `active_context`. Verified as current. |
| 2025-06-01 | Alembic templates                        | The directory `templates/alembic/alembic/versions/` contains the correct initial migration file (`3d3360227021_create_initial_conport_tables_v2.py`) and the new migration for additional tables (`5cf9ea8bcc0b_add_custom_data_and_history_tables.py`). |
| 2025-06-01 | Repository cleanup                       | Removed root-level duplicate files (`3d3360227021_create_initial_conport_tables_v2.py`, `CONPORT_FULL_TEST_REPORT.md`). Commit `b15e58b`. |
| 2025-06-01 | `src.context_portal_mcp.db.orm_models` & Alembic | • Completed ORM definitions for `CustomData`, `ProgressEntry`, `SystemPattern`, `ContextLink`, and history tables in `orm_models.py`.<br>• Generated new Alembic migration `5cf9ea8bcc0b_add_custom_data_and_history_tables.py` to include these tables and necessary schema updates.<br>• Verified initial migration `3d3360227021_...` is current before generating new one. |

> After these fixes, ConPort initializes the database in a clean workspace without errors and properly maintains context change history, including full support for custom_data.