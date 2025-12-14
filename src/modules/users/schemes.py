from sqlmodel import SQLModel
from uuid import UUID


class GetUserResponse(SQLModel):
    """Response scheme for getting a user"""
    id: UUID
    role: str
    telegram_id: int
    first_name: str
    last_name: str
    username: str


class CreateUserRequest(SQLModel):
    """Request scheme for creating a user"""
    role: str
    telegram_id: int
    first_name: str
    last_name: str
    username: str


class CreateUserResponse(SQLModel):
    """Response scheme for creating a user"""
    id: UUID
    role: str
    telegram_id: int
    first_name: str
    last_name: str
    username: str


class UpdateUserRequest(SQLModel):
    """Request scheme for updating a user"""
    role: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UpdateUserResponse(SQLModel):
    """Response scheme for updating a user"""
    id: UUID
    role: str
    telegram_id: int
    first_name: str
    last_name: str
    username: str
