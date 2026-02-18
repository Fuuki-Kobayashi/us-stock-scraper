import os
from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Resolve relative SQLite path to absolute (relative to project root)
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_db_url = settings.DATABASE_URL
_prefix = "sqlite+aiosqlite:///"
if _db_url.startswith(_prefix):
    _db_path = _db_url[len(_prefix):]
    if _db_path and not os.path.isabs(_db_path):
        _abs_db_path = os.path.join(_project_root, _db_path)
        os.makedirs(os.path.dirname(_abs_db_path), exist_ok=True)
        _db_url = f"{_prefix}{_abs_db_path}"

engine = create_async_engine(
    _db_url,
    echo=False,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
