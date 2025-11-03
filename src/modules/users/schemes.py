from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID


# class BaseUser(SQLModel, table=False):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     role: str = Field(index=True, description="Role of the user in the system")
#     created_at: datetime = Field(
#         default_factory=datetime.utcnow, description="Timestamp when the user was created")


# class BaseTelegramUser(BaseUser, table=True):
#     __tablename__ = "telegram_users"  # type: ignore

#     telegram_id: int = Field(unique=True, index=True)
#     first_name: str = Field(description="First name of the Telegram user")
#     last_name: str = Field(description="Last name of the Telegram user")
#     username: str = Field(
#         index=True, description="Telegram username of the user gotten from Telegram API")

#     operator: Optional["Operator"] = Relationship(back_populates="user")
#     client: Optional["Client"] = Relationship(back_populates="user")


# class Operator(SQLModel, table=True):
#     __tablename__ = "operators"  # type: ignore

#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     user_id: UUID = Field(foreign_key="telegram_users.id", unique=True)

#     type: str = Field(
#         description="Department the operator belongs to: admin, teacher")

#     user: Optional[BaseTelegramUser] = Relationship(back_populates="operator")


# class Client(SQLModel, table=True):
#     __tablename__ = "clients"  # type: ignore

#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     user_id: UUID = Field(foreign_key="telegram_users.id", unique=True)

#     user: Optional["BaseTelegramUser"] = Relationship(back_populates="client")

#     parent: Optional["Parent"] = Relationship(back_populates="client")
#     student: Optional["Student"] = Relationship(back_populates="client")


# class Student(SQLModel, table=True):
#     __tablename__ = "students"  # type: ignore

#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     client_id: UUID = Field(foreign_key="clients.id", unique=True)

#     parent_name: str = Field(
#         default=None, description="Name of the student's parent")
#     group_id: UUID = Field(default=None, foreign_key="groups.id",
#                            description="ID of the group the student belongs to")

#     client: Client = Relationship(back_populates="student")
#     group: "Group" = Relationship(back_populates="students")
#     tasks: list["Task"] = Relationship(back_populates="student")


# class Parent(SQLModel, table=True):
#     __tablename__ = "parents"  # type: ignore

#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     client_id: UUID = Field(foreign_key="clients.id", unique=True)
#     child_count: int = Field(default=1)

#     tasks: list["Task"] = Relationship(back_populates="parent")

#     client: Client = Relationship(back_populates="parent")

class GetUserResponse(SQLModel):
    id: UUID
    role: str
    telegram_id: int
    first_name: str
    last_name: str
    username: str

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