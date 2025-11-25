from typing import List
from fastapi import APIRouter as Router, HTTPException


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


@router.get("/submitted",
            status_code=200,
            response_model=List[TaskReadResponse],
            description="Get all tasks submitted for review")
async def get_submitted_tasks_route(session: DbSession):  # type: ignore
    tasks = await repo.read_submitted_tasks(session)
    return tasks


@router.get("/overdue",
            status_code=200,
            # response_model=List[TaskReadResponse],
            description="Get all overdue tasks")
async def get_overdue_tasks_route(session: DbSession):  # type: ignore
    """Get all tasks that are overdue but not marked as overdue yet"""
    print("Fetching overdue tasks via route...")
    tasks = await repo.read_overdue_tasks(session)
    # print("Fetched overdue tasks:", tasks)
    return tasks


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

    # Get student by user_id and use their student.id for assignment
    client = await user_repo.read_client_by_user_id(user_id, session)
    if client is None:
        raise HTTPException(status_code=404, detail="User not found")

    task = await repo.assign_task_to_user_repo(task, client.id, session)
    return task


@router.post("/{task_id}/unassign/{user_id}")
async def unassign_task_from_user(task_id: UUID, user_id: UUID, session: DbSession):  # type: ignore
    """
    Unassign a task from a student by their user_id (Telegram user ID).
    Verifies that the task is assigned to this specific student before unassigning.
    """
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get student by user_id to verify the task is assigned to this student
    student = await user_repo.read_student_by_user_id(user_id, session)
    if student is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Compare student.id (stored in DB) with task.student_id, not user_id
    if task.student_id != student.id:
        raise HTTPException(status_code=400, detail="Task is not assigned to this student")

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


@router.post("/{task_id}/submit",
             status_code=200,
             response_model=TaskReadResponse,
             description="Student submits task result for review")
async def submit_task(task_id: UUID, submit_data: TaskSubmitRequest, session: DbSession):  # type: ignore
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status not in ["pending", "in_progress", "rejected"]:
        raise HTTPException(status_code=400, detail=f"Task cannot be submitted in {task.status} status")
    
    task = await repo.submit_task_repo(task, submit_data.result, session)
    
    # TODO: Send notification to teacher/operator
    
    return task


@router.post("/{task_id}/approve",
             status_code=200,
             response_model=TaskReadResponse,
             description="Teacher/operator approves task completion")
async def approve_task(task_id: UUID, session: DbSession):  # type: ignore
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "submitted":
        raise HTTPException(status_code=400, detail="Only submitted tasks can be approved")
    
    task = await repo.approve_task_repo(task, session)
    
    # TODO: Send notification to student about approval
    
    return task


@router.post("/{task_id}/reject",
             status_code=200,
             response_model=TaskReadResponse,
             description="Teacher/operator rejects task, extends deadline by 1 hour")
async def reject_task(task_id: UUID, reject_data: TaskRejectRequest, session: DbSession):  # type: ignore
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "submitted":
        raise HTTPException(status_code=400, detail="Only submitted tasks can be rejected")
    
    task = await repo.reject_task_repo(task, reject_data.rejection_comment, session)
    
    # TODO: Send notification to student about rejection with comment
    
    return task




@router.post("/{task_id}/mark-overdue",
             status_code=200,
             response_model=TaskReadResponse,
             description="Mark task as overdue")
async def mark_task_as_overdue_route(task_id: UUID, session: DbSession):  # type: ignore
    """Mark a specific task as overdue"""
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if task can be marked as overdue
    if task.status not in ["pending", "in_progress", "rejected"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Task with status '{task.status}' cannot be marked as overdue"
        )
    
    task = await repo.mark_task_as_overdue_repo(task, session)
    return task


@router.post("/{task_id}/mark-overdue-notification",
             status_code=200,
             description="Mark that overdue notification was sent")
async def mark_overdue_notification_route(task_id: UUID, session: DbSession):  # type: ignore
    """Mark that overdue notification was sent for this task"""
    task = await repo.read_task(task_id, session)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = await repo.mark_overdue_notification_sent_repo(task, session)
    return {"status": "ok"}






