from typing import List
from fastapi import APIRouter as Router, HTTPException
from uuid import UUID

from src.modules.tasks.schemes import TaskReadResponse
from typing import Union

from src.storages.dependencies import DbSession
from src.modules.users.schemes import *
from src.modules.users import repository as repo
from src.modules.tasks import repository as task_repo
from src.storages import models
from src.errors import NotFoundError, ValidationError, ForbiddenError
from loguru import logger

router = Router(prefix="/users", tags=["users"])


@router.get("/",
            status_code=200,
            response_model=List[GetUserResponse],
            description="Retrieve a list of all users")
async def get_all_users(db: DbSession):  # type: ignore
    logger.info("Fetching all users")
    users = await repo.read_all_users(db)
    return users


@router.post("/",
             status_code=201,
            #  response_model=CreateUserResponse,
             description="Create a new user")
async def create_user(user: CreateUserRequest, db: DbSession):  # type: ignore
    user_validated = models.User.model_validate(user)
    user_created = None

    if user_validated.role == "STUDENT":
        logger.info("Creating student user")
        user_created = await repo.add_client(user_validated, db)
        
    elif user_validated.role == "OPERATOR":
        logger.info("Creating operator user")
        user_created = await repo.add_operator(user_validated, db)
    else:
        logger.warning(f"Unsupported role: {user_validated.role}")
        raise ValidationError(message="Неподдерживаемая роль")

    return user_created


@router.get("/{user_id}",
            status_code=200,
            response_model=GetUserResponse,
            description="Retrieve a specific user by their ID")
async def get_user(user_id: Union[UUID, int], db: DbSession):  # type: ignore
    user = None
    if isinstance(user_id, int):
        logger.info(f"Fetching user by Telegram ID: {user_id}")
        user = await repo.read_user_by_telegram_id(user_id, db)
    else:
        logger.info(f"Fetching user by ID: {user_id}")
        user = await repo.read_user_by_id(user_id, db)

    if user is None:
        logger.warning(f"User not found: {str(user_id)[:5]}...")
        raise NotFoundError("user")
    
    return user

@router.get("/client/telegram/{telegram_id}/group",
            status_code=200,
            # response_model=GetUserResponse,
            description="Retrieve a specific client user by their Telegram ID")
async def get_client_group_by_telegram_id(telegram_id: int, db: DbSession):  # type: ignore
    logger.info(f"Fetching client group by Telegram ID: {telegram_id}")
    client = await repo.read_client_by_telegram_id(telegram_id, db)
    if client is None:
        logger.warning(f"Client not found: {telegram_id}")
        raise NotFoundError("client")
    return client.group_id


@router.delete("/{user_id}",
               status_code=204,
               description="Delete a specific user by their ID")
async def delete_user(user_id: Union[UUID, int], db: DbSession):  # type: ignore
    logger.info(f"Deleting user: {user_id}")
    user = None
    if isinstance(user_id, int):
        user = await repo.read_user_by_telegram_id(user_id, db)
    else:
        user = await repo.read_user_by_id(user_id, db)
    if user is None:
        logger.warning(f"User not found for deletion: {user_id}")
        raise NotFoundError("user")

    await repo.delete_user_repo(user, db)
    return user


@router.patch("/{user_id}",
            status_code=200,
            response_model=UpdateUserResponse,
            description="Update a specific user by their ID")
async def update_user(user_id: UUID, user_data: UpdateUserRequest, db: DbSession):  # type: ignore
    logger.info(f"Updating user: {user_id}")
    existing_user = await repo.read_user_by_id(user_id, db)
    if existing_user is None:
        logger.warning(f"User not found for update: {user_id}")
        raise NotFoundError("user")

    updated_user = await repo.update_user_repo(existing_user, user_data, db)
    return updated_user



@router.get("/{user_id}/tasks",
            status_code=200,
            response_model=List[TaskReadResponse],
            description="Get all tasks assigned to a specific user")
async def get_student_tasks(user_id: Union[UUID, int], session: DbSession, sort: str = None):  # type: ignore
    logger.info(f"Fetching tasks for user: {user_id}")
    user = None
    if isinstance(user_id, int):
        user = await repo.read_user_by_telegram_id(user_id, session)
    else:
        user = await repo.read_user_by_id(user_id, session)
    
    if user is None:
        logger.warning(f"User not found: {user_id}")
        raise NotFoundError("user")
    
    if user.role != "STUDENT":
        logger.warning(f"User {user_id} is not a student")
        raise ForbiddenError(role="не студент")

    if isinstance(user_id, int):
        client = await repo.read_client_by_telegram_id(user_id, session)
    else:
        client = await repo.read_client_by_user_id(user_id, session)
    if client is None:
        logger.warning(f"Client not found: {user_id}")
        raise NotFoundError("client")

    tasks = None
    if sort is None:
        tasks = await task_repo.read_tasks_by_student(client.id, session)
    elif sort == "start_time":
        tasks = await task_repo.read_tasks_by_student_sort_start_time(client.id, session)
    elif sort == "end_time":
        tasks = await task_repo.read_tasks_by_student_sort_end_time(client.id, session)
    elif sort == "status":
        tasks = await task_repo.read_tasks_by_student_sort_status(client.id, session)
    else:
        logger.warning(f"Unsupported sort field: {sort}")
        raise ValidationError(message="Неподдерживаемое поле сортировки")

    return tasks
