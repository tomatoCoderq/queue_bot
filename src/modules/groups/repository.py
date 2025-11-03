from typing import List
from fastapi import APIRouter as Router

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlmodel import select
from src.config import settings

from src.storages.models import Task
from src.modules.tasks.schemes import *
from src.storages.dependencies import DbSession
from src.storages.models import *


async def add_new_group(group: Group, db: DbSession):  # type: ignore
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


async def read_all_groups(db: DbSession):  # type: ignore
    result = await db.execute(select(Group))
    return result.scalars().all()


async def read_group(group_id: UUID, db: DbSession):  # type: ignore
    result = await db.execute(select(Group).where(Group.id == group_id))
    return result.scalar()


async def add_student_to_group(group: Group, student: Student, db: DbSession):  # type: ignore
    group.students.append(student)
    await db.commit()
    await db.refresh(group)
    return group


async def remove_student(group: Group, student: Student, db: DbSession):  # type: ignore
    group.students.remove(student)
    await db.commit()
    await db.refresh(group)
    return group


async def get_tasks(group: Group, db: DbSession):  # type: ignore
    result = await db.execute(select(Task).where(Task.group == group))
    return result.scalars().all()
