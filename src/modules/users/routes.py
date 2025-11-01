from fastapi import APIRouter as Router

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import settings

router = Router(prefix="/users", tags=["users"])


@router.get("/",
            status_code=200)
async def get_all_users(db: DbSession, feedback_id: str):  # type: ignore
    pass

@router.post("/")
async def create_user(db: DbSession,  # type: ignore
                      ):
    pass

@router.get("/{user_id}")
async def get_user():
    pass

@router.delete("/{user_id}")
async def delete_user():
    pass

@router.put("/{user_id}")
async def update_user():
    pass