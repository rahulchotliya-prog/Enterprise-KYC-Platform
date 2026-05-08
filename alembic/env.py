from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

from src.database.base import Base
from src.database.models import *
from src.config.settings import settings

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------------------------
# DATABASE URL
# -------------------------------------------------------------------

# First try environment variable from Docker
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to settings if env variable missing
if not DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL

print("DATABASE_URL =", DATABASE_URL)

# Convert asyncpg URL -> psycopg2 sync URL for Alembic
SYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql+asyncpg",
    "postgresql+psycopg2"
)

print("SYNC_DATABASE_URL =", SYNC_DATABASE_URL)

# IMPORTANT: override alembic.ini value
config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)

# Metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.
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
    """
    Run migrations in online mode.
    """

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()