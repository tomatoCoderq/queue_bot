from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class FileUploadResponse(BaseModel):
    """Response scheme for file upload"""
    id: UUID
    filename: str
    type: str
    path: str
    file_id: str
    task_id: Optional[UUID]
    uploaded_at: datetime


class FileReadResponse(BaseModel):
    """Response scheme for getting file information"""
    id: UUID
    filename: str
    type: str
    path: str
    file_id: str
    task_id: Optional[UUID]
    uploaded_at: datetime