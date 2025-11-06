import httpx
from typing import Optional, Dict, Any
from loguru import logger
import os
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
        
