import logging
import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger("resumemate.database")
logging.basicConfig(level=logging.INFO)

Base = declarative_base()

# Active engine and session factory
engine = None
AsyncSessionLocal = None
ACTIVE_DB_TYPE = "unknown"

async def setup_database():
    """Initializes the database engine with PostgreSQL or graceful SQLite fallback."""
    global engine, AsyncSessionLocal, ACTIVE_DB_TYPE
    
    postgres_url = settings.get_database_url()
    
    # Try PostgreSQL first
    try:
        logger.info(f"Attempting connection to PostgreSQL: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}...")
        test_engine = create_async_engine(postgres_url, echo=False, pool_pre_ping=True)
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        
        engine = test_engine
        AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        ACTIVE_DB_TYPE = "PostgreSQL"
        logger.info("Successfully connected to PostgreSQL database!")
        return engine
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({e}).")
        
        if settings.FALLBACK_TO_SQLITE:
            sqlite_dir = Path(__file__).resolve().parent.parent / "data"
            sqlite_dir.mkdir(parents=True, exist_ok=True)
            sqlite_path = sqlite_dir / "resume_analyzer.db"
            sqlite_url = f"sqlite+aiosqlite:///{sqlite_path.as_posix()}"
            
            logger.info(f"Using local development database: {sqlite_url}")
            logger.info("Tip: Update DB_PASSWORD in backend/.env to connect to your local PostgreSQL instance.")
            
            engine = create_async_engine(sqlite_url, echo=False)
            AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
            ACTIVE_DB_TYPE = "SQLite (Development Fallback)"
            return engine
        else:
            raise e

def get_sessionmaker():
    """Returns the active async_sessionmaker."""
    global AsyncSessionLocal
    return AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding database session."""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await setup_database()
        
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
