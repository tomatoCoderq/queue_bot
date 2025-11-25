from sqlmodel import SQLModel
from uuid import UUID

class GetUserResponse(SQLModel):
    id: UUID
    role: str
    telegram_id: int
    first_name: str
    last_name: str
    username: str
    
class GetClientResponse(SQLModel):
    id: UUID
    

class CreateUserRequest(SQLModel):
    role: str
    telegram_id: int
    first_name: str
    last_name: str
    username: str
    
class CreateUserResponse(SQLModel):
    id: UUID
    role: str
    telegram_id: int
    first_name: str
    last_name: str
    username: str

class UpdateUserRequest(SQLModel):
    role: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None

class UpdateUserResponse(SQLModel):
    id: UUID
    role: str
    telegram_id: int
    first_name: str
    last_name: str
    username: str