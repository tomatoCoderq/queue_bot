from typing import List
from fastapi import APIRouter as Router, HTTPException

from src.storages.models import Task
from src.modules.tasks.schemes import *
from src.storages.dependencies import DbSession
from src.modules.tasks import repository as repo
from src.modules.users import repository as user_repo
from src.errors import NotFoundError, ValidationError, ForbiddenError
from loguru import logger

router = Router(prefix="/tasks", tags=["tasks"])


@router.get("/",
            status_code=200,
            response_model=List[TaskReadResponse],
            description="Retrieve a list of all tasks")
async def get_all_tasks(session: DbSession):  # type: ignore
    logger.info("Fetching all tasks")
    tasks = await repo.read_all_tasks(session)
    return tasks


@router.post("/",
             status_code=201,
            #  response_model=TaskReadResponse,
             description="Create a new task")
async def create_task(session: DbSession,  # type: ignore
                      task_create: TaskCreateRequest):
    try:
        logger.info("Creating new task")
        task_validated = Task.model_validate(task_create)
        task = await repo.add_task(task_validated, session)
        return task
    except Exception as e:
        # logger.error(f"Error creating task: {e}")
        raise ValidationError(message="Ошибка при создании задачи")


@router.get("/submitted",
            status_code=200,
            response_model=List[TaskReadResponse],
            description="Get all tasks submitted for review")
async def get_submitted_tasks_route(session: DbSession):  # type: ignore
    logger.info("Fetching submitted tasks")
    tasks = await repo.read_submitted_tasks(session)
    return tasks


@router.get("/overdue",
            status_code=200,
            # response_model=List[TaskReadResponse],
            description="Get all overdue tasks")
async def get_overdue_tasks_route(session: DbSession):  # type: ignore
    """Get all tasks that are overdue but not marked as overdue yet"""
    logger.info("Fetching overdue tasks")
    tasks = await repo.read_overdue_tasks(session)
    return tasks


@router.get("/{task_id}",
            status_code=200,
            response_model=TaskReadResponse,
            description="Retrieve a specific task by its ID")
async def get_task(task_id: UUID, session: DbSession):  # type: ignore
    logger.info(f"Fetching task: {task_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")
    return task


@router.delete("/{task_id}",
               status_code=204,
               description="Delete a specific task by its ID")
async def delete_task(task_id: UUID, session: DbSession):  # type: ignore
    logger.info(f"Deleting task: {task_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found for deletion: {task_id}")
        raise NotFoundError("task")

    await repo.delete_task_repo(task, session)
    return task


@router.put("/{task_id}",
            status_code=200,
            response_model=TaskReadResponse,
            description="Update a specific task by its ID")
async def update_task(task_id: UUID, session: DbSession,  # type: ignore
                      task_update: TaskUpdateRequest):
    logger.info(f"Updating task: {task_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found for update: {task_id}")
        raise NotFoundError("task")

    task = await repo.update_task_repo(task, task_update, session)
    return task

'''

    Section for assigning/unassigning tasks to users/groups and marking as complete

'''

@router.post("/{task_id}/assign/{user_id}")
async def assign_task_to_user(task_id: UUID, user_id: UUID, session: DbSession):  # type: ignore
    logger.info(f"Assigning task {task_id} to user {user_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")

    client = await user_repo.read_client_by_user_id(user_id, session)
    if client is None:
        logger.warning(f"User not found: {user_id}")
        raise NotFoundError("user")

    task = await repo.assign_task_to_user_repo(task, client.id, session)
    return task


@router.post("/{task_id}/unassign/{user_id}")
async def unassign_task_from_user(task_id: UUID, user_id: UUID, session: DbSession):  # type: ignore
    """
    Unassign a task from a student by their user_id (Telegram user ID).
    Verifies that the task is assigned to this specific student before unassigning.
    """
    logger.info(f"Unassigning task {task_id} from user {user_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")
    
    student = await user_repo.read_student_by_user_id(user_id, session)
    if student is None:
        logger.warning(f"Student not found: {user_id}")
        raise NotFoundError("student")
    
    if task.student_id != student.id:
        logger.warning(f"Task {task_id} is not assigned to student {user_id}")
        raise ValidationError(message="Задача не назначена этому студенту")

    task = await repo.unassign_task_from_user_repo(task, session)
    return task


@router.post("/{task_id}/assign_group/{group_id}")
async def assign_task_to_group(task_id: UUID, group_id: UUID, session: DbSession):  # type: ignore
    logger.info(f"Assigning task {task_id} to group {group_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")

    task = await repo.assign_task_to_group_repo(task, group_id, session)
    return task


@router.post("/{task_id}/complete")
async def mark_task_as_complete(task_id: UUID, session: DbSession):  # type: ignore
    logger.info(f"Marking task {task_id} as complete")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")

    task = await repo.mark_task_as_complete_repo(task, session)
    return task


@router.post("/{task_id}/submit",
             status_code=200,
             response_model=TaskReadResponse,
             description="Student submits task result for review")
async def submit_task(task_id: UUID, submit_data: TaskSubmitRequest, session: DbSession):  # type: ignore
    logger.info(f"Submitting task {task_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")
    
    if task.status not in ["pending", "in_progress", "rejected"]:
        logger.warning(f"Cannot submit task {task_id} in status {task.status}")
        raise ValidationError(message=f"Задача не может быть отправлена в статусе {task.status}")
    
    task = await repo.submit_task_repo(task, submit_data.result, session)
    return task


@router.post("/{task_id}/approve",
             status_code=200,
             response_model=TaskReadResponse,
             description="Teacher/operator approves task completion")
async def approve_task(task_id: UUID, session: DbSession):  # type: ignore
    logger.info(f"Approving task {task_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")
    
    if task.status != "submitted":
        logger.warning(f"Cannot approve task {task_id} in status {task.status}")
        raise ValidationError(message="Одобрить можно только отправленные задачи")
    
    task = await repo.approve_task_repo(task, session)
    return task


@router.post("/{task_id}/reject",
             status_code=200,
             response_model=TaskReadResponse,
             description="Teacher/operator rejects task, extends deadline by 1 hour")
async def reject_task(task_id: UUID, reject_data: TaskRejectRequest, session: DbSession):  # type: ignore
    logger.info(f"Rejecting task {task_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")
    
    if task.status != "submitted":
        logger.warning(f"Cannot reject task {task_id} in status {task.status}")
        raise ValidationError(message="Отклонить можно только отправленные задачи")
    
    task = await repo.reject_task_repo(task, reject_data.rejection_comment, session)
    return task




@router.post("/{task_id}/mark-overdue",
             status_code=200,
             response_model=TaskReadResponse,
             description="Mark task as overdue")
async def mark_task_as_overdue_route(task_id: UUID, session: DbSession):  # type: ignore
    """Mark a specific task as overdue"""
    logger.info(f"Marking task {task_id} as overdue")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")
    
    if task.status not in ["pending", "in_progress", "rejected"]:
        logger.warning(f"Cannot mark task {task_id} as overdue in status {task.status}")
        raise ValidationError(
            message=f"Задача в статусе '{task.status}' не может быть отмечена как просроченная"
        )
    
    task = await repo.mark_task_as_overdue_repo(task, session)
    return task


@router.post("/{task_id}/mark-overdue-notification",
             status_code=200,
             description="Mark that overdue notification was sent")
async def mark_overdue_notification_route(task_id: UUID, session: DbSession):  # type: ignore
    """Mark that overdue notification was sent for this task"""
    logger.info(f"Marking overdue notification sent for task {task_id}")
    task = await repo.read_task(task_id, session)
    if task is None:
        logger.warning(f"Task not found: {task_id}")
        raise NotFoundError("task")
    
    task = await repo.mark_overdue_notification_sent_repo(task, session)
    return task






