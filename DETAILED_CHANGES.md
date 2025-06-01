# Detailed Changes in Fork (OleynikAleksandr/context-portal)

This document outlines the detailed changes made to files in this fork compared to the original `GreatScottyMac/context-portal` repository (version `0.2.4` baseline).

---

## 1. `pyproject.toml`

**Change:** Updated the project version to reflect its forked and patched status.

**Original Content (Relevant Snippet):**
```toml
[project]
name = "context-portal-mcp"
version = "0.2.4"
authors = [
  { name="Scott McLeod", email="contextportal@gmail.com" },
]
# ... rest of the file
```

**Content After Changes (Relevant Snippet):**
```toml
[project]
name = "context-portal-mcp"
version = "0.2.4+fork.alembic_fixes"
authors = [
  { name="Scott McLeod", email="contextportal@gmail.com" },
]
# ... rest of the file
```

**Full Content After Changes:**
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "context-portal-mcp"
version = "0.2.4+fork.alembic_fixes"
authors = [
  { name="Scott McLeod", email="contextportal@gmail.com" },
]
description = "A Model Context Protocol (MCP) server for managing structured project context."
readme = "README.md"
license = {file = "LICENSE"}
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "pydantic",
    "mcp[cli]",
    "sentence-transformers",
    "chromadb",
    "alembic", # Added for database migrations
]

[project.urls]
"Homepage" = "https://github.com/GreatScottyMac/context-portal" 

[project.scripts]
conport-mcp = "context_portal_mcp.main:cli_entry_point" 

[tool.setuptools.packages.find]
where = ["src"] 

[tool.setuptools.package-data]
"context_portal_mcp" = ["templates/**/*"]

[tool.setuptools]
include-package-data = true # Include data files specified in MANIFEST.in or package_data
```

---

## 2. `.gitignore`

**Change:** Adjusted rules to ensure Alembic template files required by the package are tracked, even if general `alembic.ini` or `alembic/` patterns are ignored elsewhere.

**Original Content (Relevant Snippet from the start of this specific modification):**
```gitignore
# ... other rules ...
alembic/
alembic.ini
# Allow Alembic templates for ConPort package
!src/context_portal_mcp/templates/alembic/alembic.ini
!src/context_portal_mcp/templates/alembic/alembic/
# ... other rules ...
```

**Content After Changes (Relevant Snippet):**
```gitignore
# ... other rules ...
alembic/
alembic.ini
# Allow Alembic templates for ConPort package
# Ensure specific template files are not ignored, even if 'alembic.ini' or 'alembic/' are generally ignored.
!src/context_portal_mcp/templates/alembic/README
!src/context_portal_mcp/templates/alembic/alembic.ini.mako
!src/context_portal_mcp/templates/alembic/env.py
!src/context_portal_mcp/templates/alembic/script.py.mako
# ... other rules ...
```
*(Note: The full `.gitignore` is extensive. The change focuses on the rules directly affecting Alembic templates.)*

---

## 3. `README.md`

**Change:** Expanded the "Verify Installation (Optional)" section under "Installation from Git Repository" to include explicit commands for running the server manually after installation, in addition to running with `--help`.

**Original Content (Relevant Snippet - lines 252-262):**
```markdown
4.  **Verify Installation (Optional):**
    Ensure your virtual environment is activated.
    - **Using `uv`:**
      ```bash
      uv run python src/context_portal_mcp/main.py --help
      ```
    - **Using standard `python`:**
      `bash
    python src/context_portal_mcp/main.py --help
    `
      This should output the command-line help for the ConPort server.
```

**Content After Changes (Relevant Snippet):**
```markdown
4.  **Verify Installation and Run Manually (Optional):**
    Ensure your virtual environment is activated.

    To verify the script can be found and to see help options:
    - **Using `uv`:**
      ```bash
      uv run python src/context_portal_mcp/main.py --help
      ```
    - **Using standard `python`:**
      ```bash
    python src/context_portal_mcp/main.py --help
      ```
      This should output the command-line help for the ConPort server.

    To run the server manually in STDIO mode from the root of the cloned `context-portal` directory (assuming your project workspace is the current directory):
    - **Using `uv`:**
      ```bash
      uv run python src/context_portal_mcp/main.py --mode stdio --workspace_id .
      ```
    - **Using standard `python` (module execution):**
      ```bash
      python -m src.context_portal_mcp.main --mode stdio --workspace_id .
      ```
    - **Using standard `python` (direct script execution):**
      ```bash
      python src/context_portal_mcp/main.py --mode stdio --workspace_id .
      ```
    Replace `.` with the actual absolute path to your project workspace if it's different from the current directory where you are running ConPort.
```
*(Note: This shows the changed block. The rest of `README.md` remains extensive and unchanged by this specific modification.)*

---

## 4. `src/context_portal_mcp/main.py`

**Change:** Added necessary imports and calls to `ensure_alembic_files_exist` for automatic Alembic file provisioning at server startup, especially for STDIO mode.

**Key Modified/Added Code Snippets:**

*Near the top (imports):*
```python
# Local imports
try:
    from .handlers import mcp_handlers # We will adapt these
    from .db import database, models # models for tool argument types
    from .db.database import ensure_alembic_files_exist # Import the provisioning function # ADDED/MODIFIED
    from .core import exceptions # For custom exceptions if FastMCP doesn't map them
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.context_portal_mcp.handlers import mcp_handlers
    from src.context_portal_mcp.db import database, models
    from src.context_portal_mcp.core import exceptions
    # Fallback import if running as a script and relative imports fail
    from src.context_portal_mcp.db.database import ensure_alembic_files_exist  # ADDED for stdio mode fix
```

*Inside `main_logic` function, within `elif args.mode == "stdio":` block:*
```python
        try:
            # from src.context_portal_mcp.core.config import get_database_path # Import happens at module level
            # Call the provisioning function at server startup
            ensure_alembic_files_exist(Path(effective_workspace_id)) # ADDED
            # get_database_path(effective_workspace_id) # EARLY VALIDATION REMOVED

            if not effective_workspace_id or not os.path.isdir(effective_workspace_id): # Basic check
                 log.error(f"STDIO mode: effective_workspace_id ('{effective_workspace_id}') is not a valid directory. Please ensure client provides a correct absolute path or sets 'cwd' appropriately if using '${{workspaceFolder}}'.")
                 sys.exit(1)

            log.info(f"STDIO mode: Using effective_workspace_id '{effective_workspace_id}'. Database directory will be created on first actual DB use.")
        except Exception as e: 
            log.error(f"Unexpected error processing effective_workspace_id '{effective_workspace_id}' in STDIO mode setup: {e}")
            sys.exit(1)
        
        # ... rest of stdio mode logic ...
```
*(Note: Only key changes are shown. The surrounding code structure is assumed to be largely the same as in the original file.)*

---

## 5. `src/context_portal_mcp/db/database.py`

**Change:** Introduced the `ensure_alembic_files_exist` function to copy Alembic templates to the workspace if they are missing. Modified `run_migrations` and `get_db_connection` to call this new function, ensuring Alembic is ready before migrations or database connections are attempted.

**Key Modified/Added Code Snippets:**

*Imports at the top:*
```python
import shutil # For copying directories # ADDED
import inspect # For getting the current file's path to find templates # ADDED
```

*New function `ensure_alembic_files_exist`:*
```python
def ensure_alembic_files_exist(workspace_root_dir: Path):
    """
    Ensures that alembic.ini and the alembic/ directory exist in the workspace root.
    If not, copies them from the server's internal templates.
    """
    alembic_ini_path = workspace_root_dir / Path("alembic.ini")
    alembic_dir_path = workspace_root_dir / Path("alembic")

    current_file_dir = Path(inspect.getfile(ensure_alembic_files_exist)).parent
    log.debug(f"ensure_alembic_files_exist: current_file_dir = {current_file_dir}")
    conport_package_root = current_file_dir.parent 
    log.debug(f"ensure_alembic_files_exist: conport_package_root = {conport_package_root}")
    template_alembic_dir = conport_package_root / "templates" / "alembic"
    log.debug(f"ensure_alembic_files_exist: template_alembic_dir = {template_alembic_dir}")

    # Check for alembic.ini
    if not alembic_ini_path.exists():
        log.debug(f"alembic.ini not found at {alembic_ini_path}. Attempting to provision.")
        source_template_ini = template_alembic_dir / "alembic.ini.mako" # Corrected to .mako
        if source_template_ini.exists():
            try:
                log.info(f"Copying missing alembic.ini (from .mako) to {alembic_ini_path}")
                shutil.copy2(source_template_ini, alembic_ini_path) # Copy .mako to .ini
                log.debug(f"alembic.ini (from .mako) copied. Exists: {alembic_ini_path.exists()}")
            except shutil.Error as e:
                log.error(f"Failed to copy alembic.ini: {e}")
                raise DatabaseError(f"Failed to provision alembic.ini: {e}")
        else:
            log.warning(f"Template alembic.ini.mako not found at {source_template_ini}. Cannot auto-provision alembic.ini.")

    # Check for alembic/ directory (containing env.py, script.py.mako etc.)
    if not alembic_dir_path.exists() or \
       not any((alembic_dir_path / f).exists() for f in ["env.py", "script.py.mako", "README"]): # Added README to check
        log.debug(f"alembic/ directory or its key contents not found at {alembic_dir_path}. Attempting to provision.")
        template_scripts_dir = template_alembic_dir / "alembic" 
        if template_scripts_dir.is_dir():
            try:
                log.info(f"Copying missing alembic/ scripts from templates to {alembic_dir_path}")
                os.makedirs(alembic_dir_path, exist_ok=True)
                for item_name in os.listdir(template_scripts_dir):
                    source_item = template_scripts_dir / item_name
                    target_item = alembic_dir_path / item_name
                    if source_item.is_file(): # Only copy files
                        shutil.copy2(source_item, target_item)
                log.debug(f"alembic/ directory contents copied. Exists: {alembic_dir_path.exists()}")
            except Exception as e: # Broader exception for os.listdir or shutil errors
                log.error(f"Failed to copy alembic/ directory contents: {e}")
                raise DatabaseError(f"Failed to provision alembic/ directory: {e}")
        else:
            log.warning(f"Template alembic/ directory not found at {template_scripts_dir}. Cannot auto-provision.")
```

*Modification in `run_migrations` function:*
```python
def run_migrations(db_path: Path, project_root_dir: Path):
    """
    Runs Alembic migrations to upgrade the database to the latest version.
    This function is called on database connection to ensure schema is up-to-date.
    """
    # Ensure Alembic files are present in the project_root_dir before proceeding
    ensure_alembic_files_exist(project_root_dir) # ADDED
    alembic_ini_path = project_root_dir / Path("alembic.ini")
    # ... rest of the function
```

*Modification in `get_db_connection` function:*
```python
def get_db_connection(workspace_id: str) -> sqlite3.Connection:
    """Gets or creates a database connection for the given workspace."""
    if workspace_id in _connections:
        return _connections[workspace_id]

    db_path = get_database_path(workspace_id)
    
    # Run migrations before connecting to ensure schema is up-to-date
    # This will create the database file if it doesn't exist
    # and also ensures alembic.ini and alembic/ are present via ensure_alembic_files_exist
    run_migrations(db_path, Path(workspace_id)) # MODIFIED (was init_db_if_needed)

    try:
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    # ... rest of the function
```
*(Note: Snippets show key additions/modifications. The `ensure_alembic_files_exist` function is shown more fully as it's new. The logic for copying `alembic.ini` from `alembic.ini.mako` and the contents of the `alembic` script directory has been detailed here to reflect the intended behavior, including corrections to check for `alembic.ini.mako` and handling file copying within the `alembic` script directory.)*

---

## 6. New Alembic Template Files

The following files were added to `src/context_portal_mcp/templates/alembic/` to enable automatic provisioning of a working Alembic environment in new workspaces.

### 6.1. `src/context_portal_mcp/templates/alembic/alembic.ini.mako`
**Content:**
```ini
# A generic, direct configuration for Alembic.
# This is a Mako template, though for this basic version, it has no Mako directives.
# It will be copied as alembic.ini to the workspace.

[alembic]
# path to migration scripts
# We will set this to point to the 'alembic' subdirectory within the templates,
# which will be copied to the workspace's root.
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone for dealing with dates without due regard for timezone
# STORES THE DATABASE IN UTC
# timezone = UTC

# sqlalchemy.url = driver://user:pass@host/dbname
# This will be overridden by the ConPort server dynamically at runtime
# to point to the correct workspace-specific database.
sqlalchemy.url = sqlite:///./placeholder_conport.db

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 6.2. `src/context_portal_mcp/templates/alembic/alembic/README`
**Content:**
```
Generic single-database configuration.
```

### 6.3. `src/context_portal_mcp/templates/alembic/alembic/env.py`
**Content:**
```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line reads the section in alembic.ini regarding logging configuration.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# For ConPort, models are defined in db.models, but direct import for autogen might be tricky
# due to dynamic DB paths. We will manage migrations manually for now by importing models
# from the application structure when generating revisions.
# When run by the application, the Base metadata will be populated.
# Ensure your models are imported somewhere before Alembic tries to use target_metadata
# for autogeneration, or ensure target_metadata is correctly populated.
# For ConPort, the schema is defined in src.context_portal_mcp.db.models.Base.metadata
# We will attempt to import it here.
try:
    from src.context_portal_mcp.db.models import Base
    target_metadata = Base.metadata
except ImportError:
    # This might happen if alembic is run from a context where src. is not on PYTHONPATH
    # In such cases, autogenerate might not fully work without manual adjustments
    # or ensuring PYTHONPATH is set up correctly for alembic CLI runs.
    target_metadata = None


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 6.4. `src/context_portal_mcp/templates/alembic/alembic/script.py.mako`
**Content:**
```python
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | SCRIPT_REVISION_TEMPLATE_DEFAULT}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "# ### commands auto generated by Alembic - please adjust! ###\n    pass\n    # ### end Alembic commands ###"}


def downgrade() -> None:
    ${downgrades if downgrades else "# ### commands auto generated by Alembic - please adjust! ###\n    pass\n    # ### end Alembic commands ###"}
```

---

## 7. `FORK_NOTES.md` (New File)

**Change:** This file was created to document the purpose and key changes of this fork.

**Full Content:**
```markdown
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
```

---