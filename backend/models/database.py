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


def _create_sqlite_engine():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "infreight.db")
    url = f"sqlite+aiosqlite:///{db_path}"
    return create_async_engine(
        url,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


async def init_db():
    """Create all tables on startup with automatic fallback to local SQLite if PostgreSQL connection fails."""
    # Import models here to register them with Base
    from models.rate_search import RateSearch, CarrierSearchResult  # noqa: F401
    from models.quote import Quote, QuoteCharge  # noqa: F401
    from models.user import User  # noqa: F401

    global _engine, _async_session
    engine = _get_engine()

    from sqlalchemy import inspect, text
    def check_and_add_columns(sync_conn):
        inspector = inspect(sync_conn)
        if 'quotes' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('quotes')]
            if 'validity_till' not in columns:
                try:
                    sync_conn.execute(text("ALTER TABLE quotes ADD COLUMN validity_till VARCHAR(50)"))
                except Exception:
                    pass
            if 'free_time' not in columns:
                try:
                    sync_conn.execute(text("ALTER TABLE quotes ADD COLUMN free_time INTEGER DEFAULT 0"))
                except Exception:
                    pass
            if 'demurrage' not in columns:
                try:
                    sync_conn.execute(text("ALTER TABLE quotes ADD COLUMN demurrage INTEGER DEFAULT 0"))
                except Exception:
                    pass
            if 'detention' not in columns:
                try:
                    sync_conn.execute(text("ALTER TABLE quotes ADD COLUMN detention INTEGER DEFAULT 0"))
                except Exception:
                    pass

        if 'carrier_search_results' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('carrier_search_results')]
            new_cols = {
                "raw_origin_input": "VARCHAR(255)",
                "raw_destination_input": "VARCHAR(255)",
                "resolved_origin_name": "VARCHAR(255)",
                "resolved_origin_locode": "VARCHAR(10)",
                "resolved_destination_name": "VARCHAR(255)",
                "resolved_destination_locode": "VARCHAR(10)",
                "submitted_origin": "VARCHAR(255)",
                "submitted_destination": "VARCHAR(255)",
                "matched_origin": "VARCHAR(255)",
                "matched_destination": "VARCHAR(255)",
                "has_port_mismatch": "BOOLEAN",
                "mismatch_warning": "TEXT",
            }
            for col_name, col_type in new_cols.items():
                if col_name not in columns:
                    try:
                        sync_conn.execute(text(f"ALTER TABLE carrier_search_results ADD COLUMN {col_name} {col_type}"))
                    except Exception:
                        pass

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(check_and_add_columns)
            print("[DATABASE] Successfully initialized database schema.")
    except Exception as err:
        url = os.getenv("DATABASE_URL", "")
        if url and "sqlite" not in url:
            print(f"[DATABASE WARNING] Failed to connect to DATABASE_URL: {err}")
            print("[DATABASE WARNING] Falling back to local SQLite database (infreight.db)...")
            _engine = _create_sqlite_engine()
            _async_session = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
            async with _engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                await conn.run_sync(check_and_add_columns)
            print("[DATABASE] Local SQLite fallback database initialized successfully.")
        else:
            raise err




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
