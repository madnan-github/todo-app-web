"""
Database connection and session management for Neon PostgreSQL.

Optimized for serverless architecture with connection pooling.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, text
from src.config import settings

# Neon PostgreSQL connection optimization
# Reference: https://neon.com/docs/connect/connection-pooling

# Transform connection string for asyncpg if needed
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Determine if we should use connection pooling
# In production (Neon), use optimized pool settings
# In development (SQLite), use minimal settings
is_production = settings.is_production() and "neon" in database_url.lower()

if is_production:
    # Production: Optimized for Neon serverless
    # - pool_size: 10 connections (recommended for serverless)
    # - max_overflow: 2 (burst capacity for spikes)
    # - pool_pre_ping: Verify connection before use
    # - pool_recycle: Recycle connections hourly to avoid stale connections
    engine = create_async_engine(
        database_url,
        echo=settings.environment == "development",
        future=True,
        pool_size=10,           # Neon recommended for serverless
        max_overflow=2,         # Burst capacity
        pool_pre_ping=True,     # Verify connections
        pool_recycle=3600,      # Recycle after 1 hour
    )
else:
    # Development: Minimal pool for SQLite or local PostgreSQL
    engine = create_async_engine(
        database_url,
        echo=settings.environment == "development",
        future=True,
    )

# Async session factory
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Initialize database tables."""
    # Import models here to ensure they're registered with SQLModel.metadata
    from src.models import User, Task, Tag, TaskTag

    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """Dependency for getting async database sessions."""
    async with async_session_maker() as session:
        yield session


async def verify_connection() -> bool:
    """
    Verify database connection is working.

    Returns True if connection is healthy, False otherwise.
    Used by /health endpoint for deep health check.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
