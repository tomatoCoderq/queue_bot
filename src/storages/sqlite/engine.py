from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from src.config import settings


async_engine = None

# get async engine
def get_async_engine():
    global async_engine
    if async_engine is None:
        async_engine = create_async_engine(settings.database.DB_URL, echo=True)
    return async_engine

# get async session maker
def get_async_session_maker():
    async_engine: AsyncEngine = get_async_engine()
    async_session_maker = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=_AsyncSession) # type: ignore
    return async_session_maker

# get async session
async def get_async_session():
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()