from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, text
from src.config import settings
from urllib.parse import urlparse, parse_qs, urlencode

def fix_database_url(original_url: str) -> str:
    """Fix database URL for Neon compatibility by removing unsupported parameters."""
    if not original_url.startswith("postgresql://"):
        return original_url

    # Parse the URL
    parsed = urlparse(original_url)

    # Parse query parameters
    query_params = parse_qs(parsed.query)

    # Remove problematic parameters that asyncpg doesn't support
    params_to_remove = ['channel_binding', 'sslmode']
    for param in params_to_remove:
        query_params.pop(param, None)

    # Reconstruct the query string
    new_query = urlencode(query_params, doseq=True)

    # Reconstruct the URL with postgresql+asyncpg scheme
    fixed_url = parsed._replace(
        scheme='postgresql+asyncpg',
        query=new_query
    ).geturl()

    return fixed_url

# Create async engine for Neon PostgreSQL
# Fix the URL to be compatible with asyncpg
database_url = fix_database_url(settings.database_url)

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
