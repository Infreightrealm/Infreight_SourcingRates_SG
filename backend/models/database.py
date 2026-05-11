"""
Database connection and session management.
Supports PostgreSQL (production) and SQLite (local dev fallback).
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

load_dotenv()


class Base(DeclarativeBase):
    pass


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL", "")

    if not url:
        # Fallback to SQLite for local development without PostgreSQL
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "infreight.db")
        return f"sqlite+aiosqlite:///{db_path}"

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


# Lazy engine initialization
_engine = None
_async_session = None


def _get_engine():
    global _engine
    if _engine is None:
        url = _get_database_url()
        if "sqlite" in url:
            # SQLite needs special handling for async
            _engine = create_async_engine(
                url,
                echo=False,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            _engine = create_async_engine(url, echo=False, pool_size=10, max_overflow=20)
    return _engine


def _get_session_maker():
    global _async_session
    if _async_session is None:
        _async_session = async_sessionmaker(_get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _async_session


async def init_db():
    """Create all tables on startup."""
    # Import models here to register them with Base
    from models.rate_search import RateSearch, CarrierSearchResult  # noqa: F401
    from models.quote import Quote, QuoteCharge  # noqa: F401

    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency for getting a database session."""
    session_maker = _get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_async_session_maker():
    """Get the session maker for use outside of FastAPI dependency injection."""
    return _get_session_maker()
