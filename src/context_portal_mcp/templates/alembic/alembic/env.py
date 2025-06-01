from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line reads the loggers section in your alembic.ini file.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# ConPort specific:
# The actual target_metadata will be dynamically set by ConPort's database module
# when it configures Alembic at runtime, based on the models defined in
# src.context_portal_mcp.db.models. This template provides a placeholder.
# from src.context_portal_mcp.db import models as conport_models # This line would cause issues if templates are copied as-is
# target_metadata = conport_models.Base.metadata
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
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )
    # ConPort specific: The sqlalchemy.url is set directly by ConPort's database module
    # into the config object before this script is called.
    # We retrieve it directly here to create the engine.
    db_url = config.get_main_option("sqlalchemy.url")
    if not db_url:
        raise ValueError("sqlalchemy.url is not set in Alembic config for online mode.")

    connectable = engine_from_config(
        {"sqlalchemy.url": db_url}, # Pass only the URL to engine_from_config
        prefix="sqlalchemy.",       # Standard prefix
        poolclass=pool.NullPool
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