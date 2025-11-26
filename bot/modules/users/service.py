import httpx
from typing import Optional, Dict, Any
from loguru import logger
from src.config import settings
from src.modules.users.schemes import *

async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10) as client:
        # Get all users and find by telegram_id
        response = await client.get(f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/{telegram_id}")
        if response.status_code == 404:
            print("User not found:", telegram_id)
            return None
        
        user = response.json()
        if user:
            print("Fetched user:", user)
            return user
        
    return None


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by UUID"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/{user_id}")
        if response.status_code == 404:
            print("User not found:", user_id)
            return None
        
        user = response.json()
        if user:
            print("Fetched user:", user)
            return user
        
    return None
        
    


async def create_user(
    telegram_id: int,
    first_name: str,
    last_name: str,
    username: str,
    role: str
) -> Optional[Dict[str, Any]]:
    user_create = CreateUserRequest(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        role=role.upper()
    )
    
    async with httpx.AsyncClient(timeout=10) as client:
        # print(user_create)
        response = await client.post(
            f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/",
            json=user_create.model_dump()
        )
        response.raise_for_status()
        
        created_user = response.json()
        logger.info(f"User created successfully: {telegram_id} with role {role}")
        return created_user
        

from typing import Optional, List, Dict, Any

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
        try:
            task_data = TaskCreateRequest(
                title=title,
                description=description,
                start_date=start_date,
                due_date=due_date
            )
        except Exception as e:
            print(f"Error creating task data: {e}")
            return None
         
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


async def get_overdue_tasks() -> List[Dict[str, Any]]:
    """Get all tasks that are overdue but not marked as overdue yet"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/overdue"
        )
        response.raise_for_status()
        tasks = response.json()
        return tasks if tasks else []
    

# TODO: check whether system can be simpflified to one without this endpoint
async def mark_task_as_overdue(task_id: str) -> bool:
    """Mark task as overdue"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/mark-overdue"
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error marking task as overdue: {e}")
        return False


async def mark_overdue_notification_sent(task_id: str) -> bool:
    """Mark that overdue notification was sent"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/mark-overdue-notification"
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error marking overdue notification: {e}")
        return False
