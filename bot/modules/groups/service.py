import httpx
from typing import Optional, List, Dict, Any
from src.config import settings

from src.modules.tasks.schemes import *
from src.modules.groups.schemes import *


async def get_all_groups() -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/groups/"
        
        response = await client.get(url)
        response.raise_for_status()
        
        groups = response.json()
        return groups if groups else []
    
async def create_group(group_data: GroupCreateRequest) -> GroupCreateResponse:
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/groups/"
        
        response = await client.post(url, json=group_data.model_dump())
        response.raise_for_status()
        
        created_group = response.json()
        return GroupCreateResponse(**created_group)

async def get_group_by_id(group_id: str) -> Optional[GroupReadResponse]:
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/groups/{group_id}?by_id=True"
        
        response = await client.get(url)
        response.raise_for_status()
        
        group = response.json()
        if group:
            return GroupReadResponse(**group)
        return None
    
async def get_group_by_name(name: str):
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/groups/{name}?by_id=False"
        
        response = await client.get(url)
        response.raise_for_status()
        
        group = response.json()
        if group:
            return GroupReadResponse(**group)
        return None

async def add_student_to_group(group_id: str, student_id: str) -> bool:
    print(group_id, student_id)
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/groups/{group_id}/student/{student_id}?by_telegram_id=True"
        
        response = await client.post(url)
        response.raise_for_status()
        
        return response.status_code == 200
    return True


async def remove_student_from_group(group_id: str, student_id: str) -> bool:
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/groups/{group_id}/student/{student_id}?by_telegram_id=True"
        
        response = await client.delete(url)
        response.raise_for_status()
        
        return response.status_code == 202

async def get_group_tasks(group_id: str) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/groups/{group_id}/tasks"
        
        response = await client.get(url)
        response.raise_for_status()
        
        tasks = response.json()
        return tasks if tasks else []

async def get_group_clients(group_id: str) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/groups/{group_id}/clients"
        
        response = await client.get(url)
        response.raise_for_status()
        
        clients = response.json()
        return clients

async def get_client_group(telegram_id: int) -> Optional[str]:
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/users/client/telegram/{telegram_id}/group"
        
        response = await client.get(url)
        response.raise_for_status()
        
        group_id = response.json()
        return group_id