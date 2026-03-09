import os
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# importa tu Base
from app.database import Base

# IMPORTA TODOS TUS MODELOS AQUÍ
from app.student.models.student import Student
from app.incidencia.models.incidencia import Incidencia



# Alembic Config
config = context.config

DATABASE_URL = os.getenv("DATABASE_URL")

config = context.config

if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata para autogenerate
target_metadata = Base.metadata


# -------------------------
# OFFLINE MODE
# -------------------------
def run_migrations_offline():
    """Run migrations in offline mode."""

    
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,          # detecta cambios de tipo
        compare_server_default=True # detecta cambios de default
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------
# ONLINE MODE (ASYNC)
# -------------------------
def do_run_migrations(connection: Connection):
    
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():

    DATABASE_URL = os.getenv("DATABASE_URL")

    config.set_main_option("sqlalchemy.url", DATABASE_URL)

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

# -------------------------
# ENTRY POINT
# -------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
