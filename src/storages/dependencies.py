from src.storages.sqlite.engine import get_async_engine, get_async_session_maker, get_async_session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from typing import Annotated
from fastapi import Depends

async def get_async_db_session():
    async for session in get_async_session():
        yield session
    
DbSession = Annotated[any, Depends(get_async_db_session)]