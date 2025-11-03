from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import model_validator
from sqlmodel import SQLModel, Field 



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
    
