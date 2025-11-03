from uuid import UUID, uuid4
from pydantic import model_validator
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timedelta


class BaseUser(SQLModel, table=False):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    role: str = Field(index=True, description="Role of the user in the system")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when the user was created")


class BaseTelegramUser(BaseUser, table=True):
    __tablename__ = "telegram_users"  # type: ignore

    telegram_id: int = Field(unique=True, index=True)
    first_name: str = Field(description="First name of the Telegram user")
    last_name: str = Field(description="Last name of the Telegram user")
    username: str = Field(
        index=True, description="Telegram username of the user gotten from Telegram API")

    operator: Optional["Operator"] = Relationship(back_populates="user")
    client: Optional["Client"] = Relationship(back_populates="user")


class Operator(SQLModel, table=True):
    __tablename__ = "operators"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="telegram_users.id", unique=True)

    type: str = Field(
        description="Department the operator belongs to: admin, teacher")

    user: Optional[BaseTelegramUser] = Relationship(back_populates="operator")


class Client(SQLModel, table=True):
    __tablename__ = "clients"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="telegram_users.id", unique=True)

    user: Optional["BaseTelegramUser"] = Relationship(back_populates="client")

    parent: Optional["Parent"] = Relationship(back_populates="client")
    student: Optional["Student"] = Relationship(back_populates="client")


class Student(SQLModel, table=True):
    __tablename__ = "students"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    client_id: UUID = Field(foreign_key="clients.id", unique=True)

    parent_name: Optional[str] = Field(
        default=None, description="Name of the student's parent")

    group_id: Optional[UUID] = Field(default=None, foreign_key="groups.id",
                           description="ID of the group the student belongs to")

    client: Client = Relationship(back_populates="student")
    group: "Group" = Relationship(back_populates="students")
    tasks: list["Task"] = Relationship(back_populates="student")


class Parent(SQLModel, table=True):
    __tablename__ = "parents"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    client_id: UUID = Field(foreign_key="clients.id", unique=True)
    child_count: int = Field(default=1)

    tasks: list["Task"] = Relationship(back_populates="parent")

    client: Client = Relationship(back_populates="parent")


class Group(SQLModel, table=True):
    __tablename__ = "groups"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, description="Name of the group")
    description: Optional[str] = Field(default= None, description="Description of the group")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when the group was created")

    '''Tasks which are related to the group'''
    tasks: list["Task"] = Relationship(back_populates="group")
    
    '''Students who are in the group'''
    students: list[Student] = Relationship(back_populates="group")


class Task(SQLModel, table=True):
    __tablename__ = "tasks"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=20, index=True,
                       description="Title of the task. Should be short")
    description: Optional[str] = Field(
        default=None, description="Description of the task")

    status: str = Field(default="pending",
                        description="Current status of the task: pending, in_progress, completed, overdue")

    created_by: Optional[UUID] = Field(default=None,
        description="ID of the user who created the task")

    # TODO: Validate here dates (not earlier than created, due time > start time, etc)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when the task was created")
    start_date: datetime = Field(
        default_factory=datetime.utcnow, description="Start date of the task")
    due_date: Optional[datetime] = Field(
        default=None, description="Due date of the task. May be null if no due date is set")

    result: Optional[str] = Field(
        default=None, description="Result or outcome of the task. May be null if not completed")

    # Task will be assigned to a student
    # However we can specify a group to which the task is assigned
    # When each student in the group will get a copy of the task assigned to them
    # And group will get the task assigned to it as well
    student_id: Optional[UUID] = Field(default=None, foreign_key="students.id",
                             description="ID of the student the task is assigned to")

    group_id: Optional[UUID] = Field(default=None, foreign_key="groups.id",
                           description="ID of the group the task is assigned to")
    
    parent_id: Optional[UUID] = Field(default=None, foreign_key="parents.id")

    student: Optional[Student] = Relationship(back_populates="tasks")
    group: Optional[Group] = Relationship(back_populates="tasks")
    parent: Optional["Parent"] = Relationship(back_populates="tasks")


    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date is None or self.due_date is None:
            return self
        
        if self.due_date is None:
            self.due_date = self.start_date + timedelta(hours=1)

        start = datetime.strptime(self.start_date, "%Y-%m-%d") # type: ignore
        due = datetime.strptime(self.due_date, "%Y-%m-%d") # type: ignore

        if start >= due:
            raise ValueError("start_date must be earlier than due_date")
        return self
    


