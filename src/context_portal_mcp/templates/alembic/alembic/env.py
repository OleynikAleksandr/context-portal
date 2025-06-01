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
# For ConPort, the schema is defined in src.context_portal_mcp.db.orm_models.Base.metadata
# We will attempt to import it here.
import os
import sys

# When alembic CLI is run, os.getcwd() should be the project root (d:/.context-portal)
# Add this to the beginning of sys.path to ensure 'src' is found.
current_working_directory = os.getcwd()
if current_working_directory not in sys.path:
    sys.path.insert(0, current_working_directory)

# For debugging, also print the path env.py *thinks* is the project root based on its location
# env.py is in .../src/context_portal_mcp/templates/alembic/alembic/env.py
# So, 5 levels up should be the project root d:/.context-portal
calculated_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
print(f"DEBUG ENV.PY: current_working_directory (os.getcwd()) = {current_working_directory}")
print(f"DEBUG ENV.PY: calculated_project_root = {calculated_project_root}")
print(f"DEBUG ENV.PY: Initial sys.path = {sys.path}")

# Check existence of key files/dirs based on CWD
models_path_from_cwd = os.path.join(current_working_directory, "src", "context_portal_mcp", "db", "orm_models.py")
print(f"DEBUG ENV.PY: Expected orm_models.py path based on CWD: {models_path_from_cwd}")
print(f"DEBUG ENV.PY: Does orm_models.py exist at CWD-based path? {os.path.exists(models_path_from_cwd)}")

src_path_from_cwd = os.path.join(current_working_directory, "src")
print(f"DEBUG ENV.PY: Expected src directory path based on CWD: {src_path_from_cwd}")
print(f"DEBUG ENV.PY: Does src directory exist at CWD-based path? {os.path.isdir(src_path_from_cwd)}")


try:
    from src.context_portal_mcp.db.orm_models import Base # Corrected import
    target_metadata = Base.metadata
    if target_metadata is None: # Should not happen if Base is imported correctly
        print("WARNING: target_metadata is None after importing Base from orm_models.")
    else:
        print("SUCCESS: Imported Base and target_metadata is set.")
except ImportError as e:
    print(f"Error importing Base from src.context_portal_mcp.db.orm_models: {e}")
    print(f"Calculated project root (based on env.py location): {calculated_project_root}")
    print(f"os.getcwd() (when alembic CLI runs): {current_working_directory}") # This will be the same as above if CWD isn't changed by alembic internals
    print(f"Current sys.path after potential modifications: {sys.path}")
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