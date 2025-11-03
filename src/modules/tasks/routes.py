from typing import List
from fastapi import APIRouter as Router, HTTPException

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import settings

from src.storages.models import Task
from src.modules.tasks.schemes import *
from src.storages.dependencies import DbSession
from src.modules.tasks import repository as repo
from src.modules.users import repository as user_repo

router = Router(prefix="/tasks", tags=["tasks"])


@router.get("/",
            status_code=200,
            response_model=List[TaskReadResponse],
            description="Retrieve a list of all tasks")
async def get_all_tasks(session: DbSession):  # type: ignore
    tasks = await repo.read_all_tasks(session)
    return tasks


@router.post("/",
             status_code=201,
             response_model=TaskReadResponse,
             description="Create a new task")
async def create_task(session: DbSession,  # type: ignore
                      task_create: TaskCreateRequest):
    task_validated = Task.model_validate(task_create)
    task = await repo.add_task(task_validated, session)
    return task


@router.get("/{task_id}",
            status_code=200,
            response_model=TaskReadResponse,
            description="Retrieve a specific task by its ID")
async def get_task(task_id: UUID, session: DbSession):  # type: ignore
    task = await repo.read_task(task_id, session)
    return task


@router.delete("/{task_id}",
               status_code=204,
               description="Delete a specific task by its ID")
async def delete_task(task_id: UUID, session: DbSession):  # type: ignore
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await repo.delete_task_repo(task, session)
    return task


@router.put("/{task_id}",
            status_code=200,
            response_model=TaskReadResponse,
            description="Update a specific task by its ID")
async def update_task(task_id: UUID, session: DbSession,  # type: ignore
                      task_update: TaskUpdateRequest):
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = await repo.update_task_repo(task, task_update, session)
    return task

'''

    Section for assigning/unassigning tasks to users/groups and marking as complete

'''

@router.post("/{task_id}/assign/{user_id}")
async def assign_task_to_user(task_id: UUID, user_id: UUID, session: DbSession):  # type: ignore
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Just verify the user exists
    student = await user_repo.read_user_by_id(user_id, session)
    if student is None:
        raise HTTPException(status_code=404, detail="User not found")

    task = await repo.assign_task_to_user_repo(task, student.id, session)
    return task


@router.post("/{task_id}/unassign/{user_id}")
async def unassign_task_from_user(task_id: UUID, user_id: UUID, session: DbSession):  # type: ignore
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.student_id != user_id:
        raise HTTPException(status_code=400, detail="Task is not assigned to this user")

    task = await repo.unassign_task_from_user_repo(task, session)
    return task


@router.post("/{task_id}/assign_group/{group_id}")
async def assign_task_to_group(task_id: UUID, group_id: UUID, session: DbSession):  # type: ignore
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task = await repo.assign_task_to_group_repo(task, group_id, session)
    return task


@router.post("/{task_id}/complete")
async def mark_task_as_complete(task_id: UUID, session: DbSession):  # type: ignore
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task = await repo.mark_task_as_complete_repo(task, session)
    return task




