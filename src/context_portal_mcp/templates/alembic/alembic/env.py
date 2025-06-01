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