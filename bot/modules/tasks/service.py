import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.config import settings

from src.modules.tasks.schemes import *


async def get_student_tasks(
    telegram_id: int, 
    sort_by: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all tasks for a specific student by telegram_id
    
    Args:
        telegram_id: Telegram ID of the student
        sort_by: Sort type - 'start_time', 'end_time', 'status', or None
    
    Returns:
        List of tasks
    """
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/{telegram_id}/tasks"
        
        # Add sort parameter if provided
        params = {}
        if sort_by:
            params["sort"] = sort_by
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        tasks = response.json()
        return tasks if tasks else []


async def get_task_by_id(task_id: str) -> Optional[Dict[str, Any]]:
    """Get specific task details by task_id"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}"
        )
        response.raise_for_status()
        task = response.json()
        return task


async def get_all_students() -> List[Dict[str, Any]]:
    """Get all users with role 'student'"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/"
        )
        response.raise_for_status()
        users = response.json()
        
        # Filter only students
        students = [user for user in users if user.get("role", "").lower() == "student"]
        return students


async def create_task_and_assign(
    title: str,
    description: str,
    start_date: str,
    due_date: Optional[str],
    student_telegram_id: int
) -> Optional[Dict[str, Any]]:
    """
    Create a new task and immediately assign it to a student.
    
    Args:
        title: Task title
        description: Task description
        start_date: Start date in YYYY-MM-DD format
        due_date: Due date in YYYY-MM-DD format (optional)
        student_telegram_id: Telegram ID of the student
    
    Returns:
        Created and assigned task, or None if failed
    """
    async with httpx.AsyncClient(timeout=10) as client:
        # Step 1: Create task
        # task_data = {
        #     "title": title,
        #     "description": description,
        #     "start_date": start_date,
        #     "due_date": due_date,
        # }
        
        # start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        # due_dt = None
        # if due_date and due_date != "Не указано":
        #     due_dt = datetime.strptime(due_date, "%Y-%m-%d %H:%M")
        print("Start and end dates:", start_date, due_date)
        task_data = TaskCreateRequest(
            title=title,
            description=description,
            start_date=start_date,
            due_date=due_date
        )
         
        create_response = await client.post(
            f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/",
            json=task_data.model_dump(exclude_none=True)
        )
        create_response.raise_for_status()
        created_task = create_response.json()
        
        task_id = created_task.get("id")
        if not task_id:
            return None
        
        # Step 2: Get user_id (UUID) from telegram_id
        user_response = await client.get(
            f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/{student_telegram_id}"
        )
        user_response.raise_for_status()
        user = user_response.json()
        
        user_id = user.get("id")
        if not user_id:
            return None
        
        # Step 3: Assign task to student
        assign_response = await client.post(
            f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/assign/{user_id}"
        )
        assign_response.raise_for_status()
        assigned_task = assign_response.json()
        
        return assigned_task


async def submit_task_result(task_id: str, result: str) -> bool:
    """
    Submit task result for review
    
    Args:
        task_id: ID of the task to submit
        result: Result text from student
    
    Returns:
        True if successful, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/submit",
                json={"result": result}
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error submitting task: {e}")
        return False


async def approve_task(task_id: str) -> bool:
    """
    Approve task completion
    
    Args:
        task_id: ID of the task to approve
    
    Returns:
        True if successful, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/approve"
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error approving task: {e}")
        return False


async def reject_task(task_id: str, rejection_comment: str) -> bool:
    """
    Reject task with comment
    
    Args:
        task_id: ID of the task to reject
        rejection_comment: Comment explaining why task was rejected
    
    Returns:
        True if successful, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/reject",
                json={"rejection_comment": rejection_comment}
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error rejecting task: {e}")
        return False


async def get_submitted_tasks() -> List[Dict[str, Any]]:
    """Get all tasks with status 'submitted' for review"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/submitted"
            )
            response.raise_for_status()
            tasks = response.json()
            return tasks if tasks else []
    except Exception as e:
        print(f"Error getting submitted tasks: {e}")
        return []

