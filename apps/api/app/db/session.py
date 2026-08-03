from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Determine SSL mode for PostgreSQL connections
# Fly.io internal networking requires ssl=disable for private connections
connect_args = {}
if settings.database_url.startswith("postgresql"):
    connect_args["ssl"] = "disable"

engine = create_async_engine(settings.database_url, echo=False, connect_args=connect_args)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()