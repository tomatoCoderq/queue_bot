from fastapi import APIRouter as Router

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import settings

router = Router(prefix="/groups", tags=["groups"])

@router.post("/")
async def add_new_group():
    pass

@router.get("/")
async def get_all_groups():
    pass

@router.get("/{group_id}")
async def get_group():
    pass

@router.post("/{group_id}/student/{student_id}")
async def add_student_to_group():
    pass


@router.delete("/{group_id}/student/{student_id}")
async def remove_student_from_group():
    pass

@router.get("/{group_id}/tasks")
async def get_group_tasks():
    pass





