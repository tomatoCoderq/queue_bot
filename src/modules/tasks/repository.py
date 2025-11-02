from typing import List
from fastapi import APIRouter as Router

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlmodel import select
from src.config import settings

from src.storages.models import Task 
from src.modules.tasks.schemes import *
from src.storages.dependencies import DbSession

router = Router(prefix="/tasks", tags=["tasks"])

async def read_all_tasks(session: DbSession):  # type: ignore
    tasks = await session.execute(select(Task))
    return tasks.scalars().all()
    

@router.post("/")
async def create_task():
    pass

@router.get("/{task_id}")
async def get_task():
    pass

@router.delete("/{task_id}")
async def delete_task():
    pass

@router.put("/{task_id}")
async def update_task():
    pass

@router.post("/{task_id}/assign/{user_id}")
async def assign_task_to_user():
    pass

@router.post("/{task_id}/unassign/{user_id}")
async def unassign_task_from_user():
    pass

@router.post("/{task_id}/assign_group/{group_id}")
async def assign_task_to_group():
    pass

@router.post("/{task_id}/complete")
async def mark_task_as_complete():
    pass


