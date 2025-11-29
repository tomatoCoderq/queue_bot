from uuid import UUID, uuid4
from pydantic import field_validator, model_validator
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    username: Optional[str] = Field(
        default=None, index=True, description="Telegram username of the user gotten from Telegram API")

    first_name: str = Field()
    last_name: str = Field()
    role: str = Field(index=True, description="Role of the user in the system")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the user was created"
    )


class Client(SQLModel, table=True):
    __tablename__ = "clients"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)

    group_id: Optional[UUID] = Field(default=None, foreign_key="groups.id",
                                     description="ID of the group the client is associated with")

    tasks: list["Task"] = Relationship(back_populates="client")
    group: Optional["Group"] = Relationship(back_populates="clients")



class Operator(SQLModel, table=True):
    __tablename__ = "operators"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)


class Group(SQLModel, table=True):
    __tablename__ = "groups"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, description="Name of the group")
    description: Optional[str] = Field(
        default=None, description="Description of the group")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the group was created"
    )

    '''Tasks which are related to the group'''
    tasks: list["Task"] = Relationship(back_populates="group")

    '''Students who are in the group'''
    clients: list[Client] = Relationship(
        back_populates="group",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Task(SQLModel, table=True):
    __tablename__ = "tasks"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=20, index=True,
                       description="Title of the task. Should be short")
    description: Optional[str] = Field(
        default=None, description="Description of the task")

    status: str = Field(default="pending",
                        description="Current status of the task: pending, in_progress, submitted, completed, rejected, overdue")

    created_by: Optional[UUID] = Field(default=None,
                                       description="ID of the user who created the task")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the task was created"
    )
    start_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Start date of the task"
    )
    due_date: Optional[datetime] = Field(
        default=None, description="Due date of the task. May be null if no due date is set"
    )

    result: Optional[str] = Field(
        default=None, description="Result or outcome of the task. May be null if not completed")

    rejection_comment: Optional[str] = Field(
        default=None, description="Comment from teacher when task is rejected. Student needs to redo the task")

    overdue_notification_sent: bool = Field(
        default=False, description="Whether overdue notification was sent to client")

    client_id: Optional[UUID] = Field(default=None, foreign_key="clients.id",
                                       description="ID of the client the task is assigned to")

    group_id: Optional[UUID] = Field(default=None, foreign_key="groups.id",
                                     description="ID of the group the task is assigned to")

    client: Optional[Client] = Relationship(back_populates="tasks")
    group: Optional[Group] = Relationship(back_populates="tasks")

    @field_validator("start_date", mode="after")
    @classmethod
    def adjust_start_date(cls, v, info):
        if v is None:
            return v
        start_date_moscow = v.astimezone(ZoneInfo("Europe/Moscow"))
        new_time = start_date_moscow - timedelta(hours=3)  # Adjusting to UTC
        return new_time.replace(tzinfo=timezone.utc)

    @field_validator("due_date", mode="after")
    @classmethod
    def adjust_due_date(cls, v, info):
        if v is None:
            return v
        due_date_moscow = v.astimezone(ZoneInfo("Europe/Moscow"))
        new_time = due_date_moscow - timedelta(hours=3)
        return new_time.replace(tzinfo=timezone.utc)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date is None or self.due_date is None:
            return self

        if self.due_date is None:
            self.due_date = self.start_date + timedelta(hours=1)

        if self.start_date < self.created_at:
            raise ValueError("start_date must not be earlier than created_at")

        if self.start_date >= self.due_date:
            raise ValueError("start_date must be earlier than due_date")

        return self


class StoredFiles(SQLModel, table=True):
    __tablename__ = "stored_files"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    filename: str = Field(description="Original name of the file")
    type: str = Field(description="Type of the file: photo, document, etc.")
    file_id: str = Field(
        description="File identifier from Telegram API")
    task_id: UUID = Field(foreign_key="tasks.id",
                          description="ID of the task the file is associated with")
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the file was uploaded"
    )
    path: str = Field(description="Path where the file is stored locally or in cloud storage")
    