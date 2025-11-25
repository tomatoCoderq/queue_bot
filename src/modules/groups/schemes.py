from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel 



class GroupCreateRequest(SQLModel):
    name: str 
    description: Optional[str] = None

class GroupCreateResponse(SQLModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    
class GroupReadResponse(SQLModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    
class ClientReadResponse(SQLModel):
    id: UUID
    user_id: UUID
    telegram_id: int
    name: Optional[str]
    surname: Optional[str]
    
    
