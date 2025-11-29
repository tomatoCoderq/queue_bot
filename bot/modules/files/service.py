import httpx
from typing import List, Dict, Any, Optional
from uuid import UUID
from src.config import settings


async def upload_file(file_data: bytes, filename: str, file_type: str, task_id: Optional[str] = None, file_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Загрузка файла на сервер"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            files = {
                'file': (filename, file_data, 'application/octet-stream')
            }
            data = {}
            if task_id:
                data['task_id'] = task_id
                data['file_id'] = file_id
                data['type'] = file_type
            
            url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/files/"
            
            response = await client.post(url, files=files, data=data)
            response.raise_for_status()
            
            return response.json()
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP error uploading file: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None


async def get_task_files(task_id: str) -> List[Dict[str, Any]]:
    """Получение файлов задачи"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/files/task/{task_id}"
            
            response = await client.get(url)
            response.raise_for_status()
            
            return response.json()
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP error getting task files: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        print(f"Error getting task files: {e}")
        return []


async def delete_file(file_id: str) -> bool:
    """Удаление файла"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"http://{settings.api.API_HOST}:{settings.api.API_PORT}/files/{file_id}"
            
            response = await client.delete(url)
            response.raise_for_status()
            
            return response.status_code == 204
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP error deleting file: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False