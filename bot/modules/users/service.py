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
            logger.warning(f"User not found: {telegram_id}")
            return None
        
        user = response.json()
        if user:
            logger.info(f"Fetched user: {user.get('id')}")
            return user
        
    return None


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by UUID"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/{user_id}")
        if response.status_code == 404:
            logger.warning(f"User not found: {user_id}")
            return None
        
        user = response.json()
        if user:
            logger.info(f"Fetched user: {user.get('id')}")
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
    """Get all tasks for a student by telegram_id"""
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
    """Get task details by task_id"""
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


async def delete_student(telegram_id: int) -> bool:
    """Delete student by telegram_id"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/{telegram_id}"
            response = await client.delete(url)

            if response.status_code in (200, 202, 204):
                logger.info(f"Student deleted successfully: {telegram_id}")
                return True

            logger.warning(f"Failed to delete student {telegram_id}: status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error deleting student {telegram_id}: {e}")
        return False


async def update_user(telegram_id: int, role: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Update user data by telegram_id"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Get user UUID first
            user = await get_user_by_id(telegram_id)
            if not user:
                logger.warning(f"User not found: {telegram_id}")
                return None
            
            user_id = user.get("id")
            
            # Prepare update data
            update_data = {}
            if role:
                update_data["role"] = role.upper()
            if first_name:
                update_data["first_name"] = first_name
            if last_name:
                update_data["last_name"] = last_name
            
            if not update_data:
                logger.warning(f"No data to update for user {telegram_id}")
                return None
            
            # Send PATCH request
            response = await client.patch(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/{user_id}",
                json=update_data
            )
            response.raise_for_status()
            
            updated_user = response.json()
            logger.info(f"User {telegram_id} updated successfully")
            return updated_user
    except Exception as e:
        logger.error(f"Error updating user {telegram_id}: {e}")
        return None


async def create_task_and_assign(
    title: str,
    description: str,
    start_date: str,
    due_date: Optional[str],
    student_telegram_id: int
) -> Optional[Dict[str, Any]]:
    """Create task and assign to student"""
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
        logger.debug(f"Start and end dates: {start_date}, {due_date}")
        try:
            task_data = TaskCreateRequest(
                title=title,
                description=description,
                start_date=start_date,
                due_date=due_date
            )
        except Exception as e:
            logger.error(f"Error creating task data: {e}")
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
    """Submit task result for review"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/submit",
                json={"result": result}
            )
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        return False


async def approve_task(task_id: str) -> bool:
    """Approve task completion"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/approve"
            )
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Error approving task: {e}")
        return False


async def reject_task(task_id: str, rejection_comment: str) -> bool:
    """Reject task with comment"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/reject",
                json={"rejection_comment": rejection_comment}
            )
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Error rejecting task: {e}")
        return False


async def get_submitted_tasks() -> List[Dict[str, Any]]:
    """Get all tasks with status 'submitted'"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/submitted"
            )
            response.raise_for_status()
            tasks = response.json()
            return tasks if tasks else []
    except Exception as e:
        logger.error(f"Error getting submitted tasks: {e}")
        return []


async def get_overdue_tasks() -> List[Dict[str, Any]]:
    """Get all overdue tasks"""
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
        logger.error(f"Error marking task as overdue: {e}")
        return False


async def mark_overdue_notification_sent(task_id: str) -> bool:
    """Mark overdue notification as sent"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/tasks/{task_id}/mark-overdue-notification"
            )
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Error marking overdue notification: {e}")
        return False
