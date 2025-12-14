from src.storages.sqlite.engine import get_async_session
from typing import Annotated
from fastapi import Depends

async def get_async_db_session():
    async for session in get_async_session():
        yield session
    
DbSession = Annotated[any, Depends(get_async_db_session)]