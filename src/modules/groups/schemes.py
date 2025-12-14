from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel 



class GroupCreateRequest(SQLModel):
    """Rquest scheme for creating a group"""
    name: str 
    description: Optional[str] = None

class GroupCreateResponse(SQLModel):
    """Response scheme for creating a group"""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    
class GroupReadResponse(SQLModel):
    """Response scheme for reading a group"""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    
class ClientReadResponse(SQLModel):
    """Response scheme for reading a client"""
    id: UUID
    user_id: UUID
    telegram_id: int
    name: Optional[str]
    surname: Optional[str]
    
    
