from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


# class FileUploadRequest(BaseModel):
#     """Схема для запроса загрузки файла"""
#     filename: str
#     file_type: str  # 'photo' or 'document'
#     file_size: int
#     task_id: Optional[UUID] = None


class FileUploadResponse(BaseModel):
    """Схема ответа при загрузке файла"""
    id: UUID
    filename: str
    type: str
    path: str
    file_id: str
    task_id: Optional[UUID]
    uploaded_at: datetime


class FileReadResponse(BaseModel):
    """Схема ответа при получении информации о файле"""
    id: UUID
    filename: str
    type: str
    path: str
    file_id: str
    task_id: Optional[UUID]
    uploaded_at: datetime


class FileLinkRequest(BaseModel):
    """Схема для привязки файла к задаче"""
    task_id: UUID