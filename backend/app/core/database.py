"""Async SQLAlchemy engine / session setup for PostgreSQL."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session per request."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all tables if they do not already exist.

    For a project of this scope, ``create_all`` is used instead of a full
    migration framework such as Alembic. Alembic can be introduced later
    if the schema needs versioned migrations.
    """
    from app import models  # noqa: F401  (ensures models are registered on Base)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()
