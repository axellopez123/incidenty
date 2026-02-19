import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from databases import Database
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


# DATABASE_URL = "postgresql+asyncpg://master:Thedoors420.@db:5432/tclsport"
DATABASE_URL = os.getenv("DATABASE_URL")


database = Database(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession  # Asegúrate de que la sesión sea asíncrona
)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

async def init_db():
    try:
        from app.auth.models.user import UserDB
        from app.company.models.company import Company
        from app.events.models.event import Event
        from app.events.models.event_sponsor import event_sponsors
        from app.sponsor.models.sponsor import Sponsor
        from app.events.models.event_categories import EventCategory
        from app.categories.models.category import Category
        
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    except Exception as  msg:
        print(msg)


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()