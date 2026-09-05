import logging
from pathlib import Path
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine, text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger("priceloop.database")

BACKEND_DIR = Path(__file__).resolve().parents[2]
SQLITE_FALLBACK_PATH = BACKEND_DIR / "test.db"

# create_engine is synchronous; strip +asyncpg if present
sync_db_url = settings.database_url_sync or settings.database_url.replace("+asyncpg", "")

if sync_db_url.startswith("sqlite"):
    engine = create_engine(sync_db_url, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(sync_db_url, connect_args={"connect_timeout": 2})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected to database at %s", sync_db_url)
    except Exception as e:
        logger.warning(
            "Could not connect to configured database (%s): %s. Falling back to local SQLite at %s",
            sync_db_url,
            e,
            SQLITE_FALLBACK_PATH,
        )
        sqlite_url = f"sqlite:///{SQLITE_FALLBACK_PATH.as_posix()}"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

