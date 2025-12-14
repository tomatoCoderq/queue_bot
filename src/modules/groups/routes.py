import uuid
from fastapi import HTTPException
from typing import List
from fastapi import APIRouter as Router


from src.storages.dependencies import DbSession

from src.modules.groups import repository as repo
from src.modules.users import repository as user_repo

from src.modules.groups.schemes import *
from src.modules.tasks.schemes import *

from src.storages.models import Group
from src.errors import NotFoundError, ValidationError
from loguru import logger

router = Router(prefix="/groups", tags=["groups"])


@router.post("/{group_id}/student/{student_id}",
             status_code=202,
             description="Add specific student as member of given group")
async def add_student_to_group(group_id: UUID, student_id: UUID | str, by_telegram_id: bool, db: DbSession):  # type: ignore
    logger.info(f"Adding student {student_id} to group {group_id}")
    group = await repo.read_group(group_id, db)
    student = None
    if by_telegram_id:
        student = await user_repo.read_user_by_telegram_id(student_id, db)
    else:
        student = await user_repo.read_user(student_id, db)

    if group is None:
        logger.warning(f"Group not found: {group_id}")
        raise NotFoundError("group")
    if student is None:
        logger.warning(f"Student not found: {student_id}")
        raise NotFoundError("student")

    updated_group = await repo.add_client_to_group(group, student, db)
    return updated_group


@router.post("/",
             status_code=201,
             response_model=GroupCreateResponse,
             description="Create a new group")
async def create_new_group(group: GroupCreateRequest, db: DbSession):  # type: ignore
    logger.info("Creating new group")
    group_model = Group.model_validate(group)
    await repo.add_new_group(group_model, db)
    return group_model


@router.get("/",
            response_model=List[GroupReadResponse],
            description="Retrieve a list of all groups")
async def get_all_groups(db: DbSession):  # type: ignore
    logger.info("Fetching all groups")
    groups = await repo.read_all_groups(db)
    return groups


# @router.get("/{name}",
#             response_model=GroupReadResponse,
#             description="Retrieve a specific group by its unique name")
# async def get_group(name: str, db: DbSession):  # type: ignore
#     group = await repo.read_group_by_name(name, db)
#     if group is None:
#         raise HTTPException(status_code=404, detail="Group not found")
#     return group


@router.get("/{input}",
            response_model=GroupReadResponse,
            description="Retrieve a specific group by its ID")
async def get_group(input: str, by_id: bool, db: DbSession):  # type: ignore
    logger.info(f"Fetching group: {input}")
    group = None
    if by_id:
        group = await repo.read_group(uuid.UUID(input), db)
    else:
        group = await repo.read_group_by_name(input, db)

    if group is None:
        logger.warning(f"Group not found: {input}")
        raise NotFoundError("group")
    return group


@router.delete("/{group_id}/student/{client_id}",
               status_code=202,
               description="Remove specific student as member of given group")
# type: ignore
async def remove_client_from_group(group_id: UUID, client_id: UUID | str, by_telegram_id: bool, db: DbSession): # type: ignore
    logger.info(f"Removing student {client_id} from group {group_id}")
    group = await repo.read_group(group_id, db)
    client = None
    if by_telegram_id:
        client = await user_repo.read_client_by_telegram_id(client_id, db)
    else:
        client = await user_repo.read_client_by_user_id(client_id, db)
    
    if group is None:
        logger.warning(f"Group not found: {group_id}")
        raise NotFoundError("group")

    if client is None:
        logger.warning(f"Student not found: {client_id}")
        raise NotFoundError("student")

    await repo.remove_client(group, client, db)


@router.get("/{group_id}/tasks",
            status_code=202,
            response_model=List[TaskReadResponse],
            description="Get all tasks which are assigned to given group")
async def get_group_tasks(group_id: UUID, db: DbSession):  # type: ignore
    logger.info(f"Fetching tasks for group: {group_id}")
    group = await repo.read_group(group_id, db)
    if group is None:
        logger.warning(f"Group not found: {group_id}")
        raise NotFoundError("group")

    tasks = await repo.get_tasks(group, db)
    return tasks


@router.get("/{group_id}/clients",
            status_code=202,
            # response_model=List[ClientReadResponse],
            description="Get all clients which are members of given group")
async def get_group_clients(group_id: UUID, db: DbSession):  # type: ignore
    logger.info(f"Fetching clients for group: {group_id}")
    group = await repo.read_group(group_id, db)
    if group is None:
        logger.warning(f"Group not found: {group_id}")
        raise NotFoundError("group")

    clients = group.clients
    users = []
    for client in clients:
        user = await user_repo.read_user_by_id(client.user_id, db)
        users.append(user)
    return users
