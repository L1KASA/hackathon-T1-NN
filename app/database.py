from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from app.common.config import settings
from app.common.logging import logger

engine = create_async_engine(
    settings.database_url,
    echo=True,
)

session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for async database session"""
    async with session_maker() as session:
        try:
            logger.debug("Database session created")
            yield session
        except Exception as exc:
            logger.error(f"Database session error: {exc}", exc_info=True)
            raise exc
        finally:
            await session.close()
            logger.debug("Database session closed")

async def initialize_db() -> None:
    """Initialize database connection"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully")
    except Exception as exc:
        logger.error(f"Failed to initialize database: {exc}", exc_info=True)
        raise

async def shutdown_db() -> None:
    """Shutdown database connection"""
    try:
        await engine.dispose()
        logger.info("Database connection closed successfully")
    except Exception as exc:
        logger.error(f"Error during database shutdown: {exc}", exc_info=True)
        raise
