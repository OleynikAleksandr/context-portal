# Notes on the ConPort Fork (OleynikAleksandr/context-portal)

## Problem: Automatic DB initialization does not create tables

**ConPort Version:** 0.2.4+fork.alembic_fixes (and subsequent fixes leading up to this)

**Description:**
When ConPort is launched for the first time in a new workspace, even though `alembic.ini`, the `alembic/` directory and the file `context_portal/context.db` are created, the database tables (e.g. `product_context`, `decisions`, etc.) are not. This results in "no such table" errors when ConPort is used.

**Cause:**
The main reason was that the package did not include the Alembic migration script files (`.py`) themselves inside the template directory `src/context_portal_mcp/templates/alembic/alembic/versions/`, which contain the instructions for creating tables. The function `ensure_alembic_files_exist` copied the Alembic directory structure, but without migration scripts `command.upgrade(cfg, "head")` could not create the tables. Additional issues with Alembic paths and configuration during autogeneration and execution of migrations were also discovered and fixed.

**Fix process (key steps):**

1. **Adjusting `ensure_alembic_files_exist` ([`src/context_portal_mcp/db/database.py`](src/context_portal_mcp/db/database.py:1)):**
   * The function was updated to recursively copy the entire contents of `src/context_portal_mcp/templates/alembic/alembic/` (including the `versions` sub-directory with migration files) into the user workspace at `[workspace_root]/alembic/`.

2. **Adjusting `run_migrations` ([`src/context_portal_mcp/db/database.py`](src/context_portal_mcp/db/database.py:1)):**
   * The `script_location` and `sqlalchemy.url` settings in the Alembic `Config` object now use absolute paths resolved from `project_root_dir` (the workspace path) and `db_path` respectively. This guarantees Alembic works correctly regardless of the current working directory of the process.
   * Added more detailed logging for path debugging.

3. **Creating and configuring Alembic templates in the ConPort package:**
   * Because the original Alembic templates were missing from `src/context_portal_mcp/templates/alembic/`, they were created:
       * `src/context_portal_mcp/templates/alembic/alembic.ini`
       * `src/context_portal_mcp/templates/alembic/alembic/script.py.mako`
       * `src/context_portal_mcp/templates/alembic/alembic/env.py`
   * `alembic.ini` is configured with `script_location = %(here)s/alembic`.
   * `env.py` was modified to correctly add paths to `sys.path` and import `Base.metadata` from the new file `src.context_portal_mcp.db.orm_models`.

4. **Creating SQLAlchemy ORM Models (`src/context_portal_mcp/db/orm_models.py`):**
   * A new file `orm_models.py` was created containing ConPort table definitions using SQLAlchemy ORM and the declarative base `Base = declarative_base()`. This is required for `alembic revision --autogenerate`. At the moment it contains only basic models; all remaining tables must still be added.

5. **Generating the initial migration file:**
   * After all of the above settings, the command was successfully executed:
     ```bash
     # In the context-portal directory with PYTHONPATH configured
     python -m alembic -c src/context_portal_mcp/templates/alembic/alembic.ini revision -m "create_initial_conport_tables" --autogenerate
     ```
   * This created the migration file (`b7798b697008_create_initial_conport_tables.py`) in `src/context_portal_mcp/templates/alembic/alembic/versions/`.
   * The template `script.py.mako` was fixed to correctly handle `down_revision = None` for the first migration.

**Result:**
Now, when ConPort is launched for the first time in a new workspace:
1. All necessary Alembic files, including migration scripts from `versions/`, are correctly copied from the package templates to `[workspace_root]/alembic/`.
2. The `run_migrations` function successfully applies those migrations to `[workspace_root]/context_portal/context.db`, creating all required tables.

**Next steps for the fork developer:**
* Complete `src/context_portal_mcp/db/orm_models.py` with all other ORM models matching the Pydantic models and intended DB schema.
* After completing `orm_models.py`, **re-generate a migration** (`python -m alembic -c src/context_portal_mcp/templates/alembic/alembic.ini revision -m "new_migration_name" --autogenerate`) so that it includes all tables. The current generated file (`b7798b697008_create_initial_conport_tables.py`) can be deleted before the new full generation, or left in place and Alembic will create an additional migration for the remaining tables.
* The `.gitkeep` file from `src/context_portal_mcp/templates/alembic/alembic/versions/` was overwritten with empty content and can be removed in the commit (or kept if it is standard practice for empty Git directories).
* Thoroughly test initialization in a clean workspace.
* Commit the changes, including the new Alembic templates and generated migration file.
---
## 2025-06-01 — Additional fixes (context history + repository cleanup)

1. **`src/context_portal_mcp/db/database.py`**  
   * The `_add_context_history_entry` function now accepts `context_id` (the row ID from the main table) and inserts it into the `product_context_id` or `active_context_id` column in the history tables.  
   * Calls to `_add_context_history_entry` in `update_product_context` and `update_active_context` were updated and pass `1` as `context_id`.  
   * The error `NOT NULL constraint failed: product_context_history.product_context_id` has been resolved.

2. **Initial Alembic migration script**  
   * The fully corrected file `3d3360227021_create_initial_conport_tables_v2.py` is placed **only** in the templates at `src/context_portal_mcp/templates/alembic/alembic/versions/`.  
   * The duplicate file in the project root was deleted; during initialization new workspaces receive exactly the correct version from the templates.

3. **Temporary files removed**  
   * `CONPORT_FULL_TEST_REPORT.md` — the detailed report was moved to internal documentation and removed from the root.  
   * The duplicate root-level migration script was deleted to avoid confusion.

4. **Commit “CLEANUP”**  
   * The changes were committed and pushed (`b15e58b`) to the `main` branch.
---

## 2025-06-01 — Fix for "no such table: custom_data"

**Problem:**
The test run (`CONPORT_TEST_PLAN_results.md`) revealed that tools related to `custom_data` (e.g., `log_custom_data`, `get_custom_data`) were failing with a "no such table: custom_data" error. This indicated that the `custom_data` table, along with potentially other related tables like history and links, were not being created by the initial Alembic migrations.

**Fix process:**

1.  **Updated SQLAlchemy ORM Models ([`src/context_portal_mcp/db/orm_models.py`](src/context_portal_mcp/db/orm_models.py:1)):**
    *   Added the `CustomDataORM` model.
    *   Added `ProductContextHistoryORM` and `ActiveContextHistoryORM` models for tracking changes to contexts.
    *   Added `ContextLinkORM` for linking various ConPort items.
    *   Added `ProgressEntryORM` and `SystemPatternORM` to complete the schema based on Pydantic models.
    *   Ensured relationships (e.g., `history`, `parent`/`children`) and constraints (e.g., `UniqueConstraint` for `custom_data`, `unique=True` for `system_patterns.name`, `ondelete="CASCADE"` for history FKs) were correctly defined.

2.  **Generated New Alembic Migration:**
    *   After updating `orm_models.py`, a new Alembic migration script (`5cf9ea8bcc0b_add_custom_data_and_history_tables.py`) was generated using `alembic revision -m "add_custom_data_and_history_tables" --autogenerate`.
    *   This script includes operations to create `custom_data`, `context_links`, `progress_entries`, `system_patterns`, and update history tables and indexes.
    *   The new migration file was added to `src/context_portal_mcp/templates/alembic/alembic/versions/`.

3.  **Initial Migration Verification:**
    *   Confirmed that the existing initial migration script (`3d3360227021_create_initial_conport_tables_v2.py`) in the distribution templates is up-to-date and does not require changes.

**Result:**
With the updated ORM models and the new migration script, ConPort will now create all necessary tables, including `custom_data`, `context_links`, `progress_entries`, and `system_patterns`, during initialization in a new workspace. This resolves the "no such table" error and enables full functionality for custom data management and other related features.
---

## 2025-06-01 — Final Alembic Adjustments and .gitignore Fix

**Problem Recap:**
Even after adding the new migration for `custom_data` and other tables, testing revealed that these tables were still not being created on a fresh initialization. Further investigation showed two issues:
1.  The initial migration script (`3d3360227021_create_initial_conport_tables_v2.py`) was using `server_default='{}'` for JSON fields, which could lead to SQLite storing it as a string, causing Pydantic validation errors (e.g., for `active_context`).
2.  The newly generated migration file (`..._add_custom_data_and_history_tables.py`) was not being committed to the repository due to an overly broad `.gitignore` rule and was therefore missing from the distribution templates.

**Fix process:**

1.  **Corrected Initial Migration Script (`...versions/3d3360227021_...py`):**
    *   Modified `server_default='{}'` to `server_default=sa.text("'{}'")` for `product_context.content` and `active_context.content` to ensure SQLite stores an actual JSON object.
    *   Updated `op.bulk_insert` for these tables to use `json.dumps({})` for the `content` value, ensuring correct JSON string insertion.

2.  **Ensured Second Migration Inclusion:**
    *   The second migration script (`2124bc786e21_add_custom_data_and_history_tables.py` - note: ID might change if regenerated) was re-generated after confirming the ORM models were correct.
    *   The `.gitignore` file was updated to correctly track all necessary Alembic template files, including all migration scripts in the `versions` subdirectory. Specifically, general rules like `alembic/` were changed to `/alembic/` (root-only), and explicit `!src/context_portal_mcp/templates/alembic/alembic/versions/*` ensure template migrations are included.
    *   The new migration script was then successfully added to Git and committed.

**Result:**
With these final adjustments:
*   The initial migration now correctly sets up default JSON values.
*   Both migration scripts (initial and the one adding `custom_data`, etc.) are now correctly included in the distribution templates and are applied sequentially during a fresh database initialization.
*   This ensures the complete database schema is created as intended, resolving all previously identified "no such table" errors and Pydantic validation issues related to initial context data.
---

## 2025-06-01 — SQLite Batch Mode for Alembic Migrations

**Problem:**
During initialization on a new workspace (attempt 2, see `conport_initialization_report_attempt_2.md`), an error occurred: `Database migration failed: No support for ALTER of constraints in SQLite dialect.` This happened even when creating the database from scratch.

**Cause:**
SQLite has limitations regarding `ALTER TABLE` operations, especially for modifying constraints. Alembic requires "batch mode" to be enabled to work around these limitations by creating a new table, copying data, dropping the old table, and renaming the new one. This mode was not enabled.

**Fix process:**

1.  **Enabled Batch Mode in Alembic (`alembic/env.py`):**
*   In the template file `src/context_portal_mcp/templates/alembic/alembic/env.py`, the `context.configure()` calls within both `run_migrations_offline()` and `run_migrations_online()` functions were updated to include `render_as_batch=True`.
*   This ensures that Alembic uses the copy-and-move strategy for migrations involving operations that SQLite doesn't natively support for `ALTER TABLE`.

**Result:**
With batch mode enabled, Alembic should now be able to correctly apply all migrations, including those that might implicitly or explicitly try to alter constraints in a way SQLite normally disallows, even during the initial creation of the database from multiple migration scripts. This is expected to resolve the `No support for ALTER of constraints in SQLite dialect` error.