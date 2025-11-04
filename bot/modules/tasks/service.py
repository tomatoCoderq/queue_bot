import httpx
from typing import Optional, List, Dict, Any
from src.config import settings


async def get_student_tasks(telegram_id: int) -> List[Dict[str, Any]]:
    """Get all tasks for a specific student by telegram_id"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/{telegram_id}/tasks"
        )
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
