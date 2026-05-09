from logging.config import fileConfig
import os
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

from src.database.base import Base
# from src.database.models import 

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load environment variables from .env if present
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
if ENV_FILE.exists():
    with ENV_FILE.open() as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key and key not in os.environ:
                os.environ[key] = value

# Find database URL from environment or alembic.ini
DATABASE_URL = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing. Set DATABASE_URL or configure sqlalchemy.url in alembic.ini."
    )

print("DATABASE_URL =", DATABASE_URL)

# Convert asyncpg URL -> psycopg2 sync URL for Alembic
SYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql+asyncpg",
    "postgresql+psycopg2",
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