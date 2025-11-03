from fastapi import HTTPException
from typing import List
from urllib import response
from fastapi import APIRouter as Router

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import settings
from src.storages.dependencies import DbSession

from src.modules.groups import repository as repo
from src.modules.users import repository as user_repo

from src.modules.groups.schemes import *
from src.modules.tasks.schemes import *

from src.storages.models import Group

router = Router(prefix="/groups", tags=["groups"])


@router.post("/",
             status_code=201,
             response_model=GroupCreateResponse,
             description="Create a new group")
async def create_new_group(group: GroupCreateRequest, db: DbSession):  # type: ignore
    group_model = Group.model_validate(group)
    await repo.add_new_group(group_model, db)
    return group_model  


@router.get("/",
            response_model=List[GroupReadResponse],
            description="Retrieve a list of all groups")
async def get_all_groups(db: DbSession):  # type: ignore
    groups = await repo.read_all_groups(db)
    return groups


@router.get("/{group_id}",
            response_model=GroupReadResponse,
            description="Retrieve a specific group by its ID")
async def get_group(group_id: UUID, db: DbSession):  # type: ignore
    group = await repo.read_group(group_id, db)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.post("/{group_id}/student/{student_id}",
             status_code=202,
             description="Add specific student as member of given group")
async def add_student_to_group(group_id: UUID, student_id: UUID, db: DbSession):  # type: ignore
    group = await repo.read_group(group_id, db)
    student = await user_repo.read_user(student_id, db)
    
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    updated_group = await repo.add_student_to_group(group, student, db)
    return updated_group


@router.delete("/{group_id}/student/{student_id}",
               status_code=202,
               description="Remove specific student as member of given group")
async def remove_student_from_group(group_id: UUID, student_id: UUID, db: DbSession):  # type: ignore
    group = await repo.read_group(group_id, db)
    student = await user_repo.read_user(student_id, db)

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")    

    await repo.remove_student(group, student, db)



@router.get("/{group_id}/tasks",
            status_code=202,
            response_model=List[TaskReadResponse],
            description="Get all tasks which are assigned to given group")
async def get_group_tasks(group_id: UUID, db: DbSession):  # type: ignore
    group = await repo.read_group(group_id, db)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    tasks = await repo.get_tasks(group, db)
    return tasks
