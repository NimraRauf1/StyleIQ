"""
STYLEIQ Database Connection
────────────────────────────
Creates the SQLAlchemy engine and session factory.
Every part of the app that needs DB access imports from here.

Usage:
    from styleiq.database.connection import get_db, engine
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from styleiq.config import settings
from styleiq.logger import get_logger

log = get_logger(__name__)


# ── Base class for all models ──────────────────────────────────────────────
class Base(DeclarativeBase):
    """
    All SQLAlchemy models inherit from this.
    Declaring it here means all models share the same metadata,
    which Alembic needs to detect schema changes.
    """
    pass


# ── Engine ─────────────────────────────────────────────────────────────────
def _create_engine():
    """Create the SQLAlchemy engine based on current config."""
    url = settings.database.url

    if settings.database.is_sqlite:
        # SQLite needs the directory to exist
        db_path = url.replace("sqlite:///", "")
        if db_path and db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},  # needed for SQLite
            echo=settings.debug,   # logs all SQL in debug mode
        )

        # Enable WAL mode for better SQLite performance
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")  # enforce foreign keys
            cursor.close()

    else:
        # PostgreSQL (future)
        engine = create_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,   # verify connections before use
            echo=settings.debug,
        )

    log.info("Database engine created | url={url}", url=url.split("@")[-1])
    return engine


engine = _create_engine()

# ── Session factory ────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # we control transactions manually
    autoflush=False,    # we control when to flush
    expire_on_commit=False,  # keep objects usable after commit
)


# ── Dependency for FastAPI (Milestone 10+) ────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Yields a database session and closes it when done.
    Used as a FastAPI dependency later.

    Usage in FastAPI:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Utility functions ──────────────────────────────────────────────────────
def create_tables() -> None:
    """Create all tables defined in models.py."""
    from styleiq.database import models  # import to register models
    Base.metadata.create_all(bind=engine)
    log.info("All database tables created")


def verify_connection() -> bool:
    """Test that the database is reachable. Returns True if OK."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log.info("Database connection verified")
        return True
    except Exception as e:
        log.error("Database connection failed: {e}", e=str(e))
        return False
