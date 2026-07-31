from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.core.config import settings

engine_options: dict = {"pool_pre_ping": True}
if settings.database_url in {
    "sqlite+aiosqlite://",
    "sqlite+aiosqlite:///:memory:",
}:
    engine_options["poolclass"] = StaticPool

engine = create_async_engine(settings.database_url, **engine_options)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
