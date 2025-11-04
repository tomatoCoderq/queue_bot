from typing import List
from fastapi import APIRouter as Router

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlmodel import select
from src.config import settings

from src.storages.models import *
from src.modules.tasks.schemes import *
from src.storages.dependencies import DbSession
from src.modules.users import repository as user_repo


async def read_all_tasks(session: DbSession):  # type: ignore
    tasks = await session.execute(select(Task))
    return tasks.scalars().all()


async def add_task(task_create: Task, session: DbSession):  # type: ignore
    session.add(task_create)
    await session.commit()
    await session.refresh(task_create)
    return task_create


async def read_task(task_id: UUID, session: DbSession):  # type: ignore
    task = await session.get(Task, task_id)
    return task


async def delete_task_repo(task: Task, session: DbSession):  # type: ignore
    await session.delete(task)
    await session.commit()


async def update_task_repo(task: Task, task_update: TaskUpdateRequest, session: DbSession):  # type: ignore
    # TODO: Maybe there is much more beaufiul way to do this?
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await session.commit()
    return task


# type: ignore
async def assign_task_to_user_repo(task: Task, student_id: UUID, session: DbSession):
    task.student_id = student_id
    await session.commit()
    await session.refresh(task)
    return task


# type: ignore
async def unassign_task_from_user_repo(task: Task, session: DbSession):
    task.student_id = None
    await session.commit()
    return task


# type: ignore
async def assign_task_to_group_repo(task: Task, group_id: UUID, session: DbSession):
    task.group_id = group_id
    await session.commit()
    return task


# type: ignore
async def mark_task_as_complete_repo(task: Task, session: DbSession):
    task.status = "completed"
    await session.commit()
    return task


async def read_tasks_by_student(student_id: UUID, session: DbSession):  # type: ignore
    print("Reading tasks for student_id:", student_id)
    statement = select(Task).where(Task.student_id == student_id)
    result = await session.execute(statement)
    # print("result:", result.scalars().all())
    return result.scalars().all()

async def read_tasks_by_student_sort_start_time(student_id: UUID, session: DbSession): # type: ignore
    statement = select(Task).where(Task.student_id == student_id).order_by(Task.start_date)
    result = await session.execute(statement)
    return result.scalars().all()

async def read_tasks_by_student_sort_end_time(student_id: UUID, session: DbSession): # type: ignore
    statement = select(Task).where(Task.student_id == student_id).order_by(Task.due_date)
    result = await session.execute(statement)
    return result.scalars().all()

async def read_tasks_by_student_sort_status(student_id: UUID, session: DbSession): # type: ignore
    statement = select(Task).where(Task.student_id == student_id).order_by(Task.status)
    result = await session.execute(statement)
    return result.scalars().all()



async def read_tasks_by_user(student: Student, session: DbSession):  # type: ignore
    if student is None:
        return []
    return await read_tasks_by_student(student.id, session)


async def submit_task_repo(task: Task, result: str, session: DbSession):  # type: ignore
    """Student submits task result for review"""
    task.result = result
    task.status = "submitted"
    await session.commit()
    await session.refresh(task)
    return task


async def approve_task_repo(task: Task, session: DbSession):  # type: ignore
    """Teacher/operator approves task completion"""
    task.status = "completed"
    await session.commit()
    await session.refresh(task)
    return task


async def reject_task_repo(task: Task, rejection_comment: str, session: DbSession):  # type: ignore
    """Teacher/operator rejects task, extends deadline by 1 hour"""
    from datetime import timedelta
    
    task.status = "rejected"
    task.rejection_comment = rejection_comment
    
    # Extend deadline by 1 hour
    if task.due_date:
        task.due_date = task.due_date + timedelta(hours=1)
    
    await session.commit()
    await session.refresh(task)
    return task


async def read_submitted_tasks(session: DbSession):  # type: ignore
    """Get all tasks with status 'submitted' for teacher review"""
    statement = select(Task).where(Task.status == "submitted")
    result = await session.execute(statement)
    return result.scalars().all()
