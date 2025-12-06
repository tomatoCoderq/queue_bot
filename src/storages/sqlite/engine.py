from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from src.config import settings
from loguru import logger

async_engine = None

def get_async_engine():
    """ Create and return async engine which uses the database URL from settings """
    global async_engine
    if async_engine is None:
        logger.debug(
            f"Creating async engine with DB URL: {settings.database.DB_URL}")
        async_engine = create_async_engine(
            settings.database.DB_URL, echo=False)  # type: ignore
    return async_engine


def get_async_session_maker():
    """Create and return async session maker. Async session maker is used to create async sessions."""
    async_engine: AsyncEngine = get_async_engine()
    logger.debug("Creating async session maker")
    async_session_maker = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncSession)  # type: ignore
    return async_session_maker

async def get_async_session():
    """Create and return an async session. Async session is used to interact with the database asynchronously."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
