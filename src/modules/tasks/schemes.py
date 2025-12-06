from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from pydantic import field_validator, model_validator
from sqlmodel import SQLModel, Field
from zoneinfo import ZoneInfo 



class TaskCreateRequest(SQLModel):
    title: str = Field(description="Title of the task")
    description: Optional[str] = Field(description="Detailed description of the task")
    start_date: str = Field(default_factory=datetime.utcnow,description="Start date for the task")
    due_date: Optional[str] = Field(default=None, description="Due date for the task in YYYY-MM-DD format")

    # @field_validator("start_date", mode="before")
    # def parse_start_date(cls, value):
    #     if value < datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"):
    #         print("ValueError raised in parse_start_date")
    #         raise ValueError("start_date must not be earlier than current time")
    #     return value

    # @field_validator("due_date", mode="before")
    # def parse_due_date(cls, value):
    #     if value < datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"):
    #         raise ValueError("due_date must not be earlier than current time")
    #     return value

    # @model_validator(mode="after")
    # def validate_dates(self):
    #     if self.start_date is None or self.due_date is None:
    #         return self
        
    #     start = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M") # type: ignore
    #     due = datetime.strptime(self.due_date, "%Y-%m-%d %H:%M") # type: ignore

    #     if start >= due:
    #         raise ValueError("start_date must be earlier than due_date")
        
    #     return self

class TaskCreateResponse(SQLModel):
    id: UUID = Field(description="Unique identifier for the task")
    title: str = Field(description="Title of the task")
    description: str = Field(description="Detailed description of the task")
    status: str = Field(description="Current status of the task")
    created_at: datetime = Field(description="Timestamp when the task was created")
    start_date: datetime = Field(description="Start date of the task")
    due_date: Optional[datetime] = Field(description="Due date for the task")
    
#TODO: Validate here dates (not earlier than created, due time > start time, etc)    
class TaskReadResponse(SQLModel):
    id: UUID = Field(description="Unique identifier for the task")
    title: str = Field(description="Title of the task")
    description: Optional[str] = Field(description="Detailed description of the task")
    status: Optional[str] = Field(description="Current status of the task")
    result: Optional[str] = Field(description="Result or outcome of the task")
    created_at: Optional[datetime] = Field(description="Timestamp when the task was created")
    start_date: Optional[datetime] = Field(description="Start date of the task")
    due_date: Optional[datetime] = Field(description="Due date for the task")
    client_id: Optional[UUID] = Field(description="ID of the client the task is assigned to")
    group_id: Optional[UUID] = Field(description="ID of the group the task is")

class TaskUpdateRequest(SQLModel):
    title: Optional[str] = Field(default=None, description="Title of the task")
    description: Optional[str] = Field(default=None, description="Detailed description of the task")
    status: Optional[str] = Field(default=None, description="Current status of the task")
    start_date: Optional[datetime] = Field(default=None, description="Start date of the task")
    due_date: Optional[datetime] = Field(default=None, description="Due date for the task")
    
    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date is None or self.due_date is None:
            return self
        
        start = datetime.strptime(self.start_date, "%Y-%m-%d") # type: ignore
        due = datetime.strptime(self.due_date, "%Y-%m-%d") # type: ignore

        if start >= due:
            raise ValueError("start_date must be earlier than due_date")
        return self

class TaskUpdateResponse(SQLModel):
    id: UUID = Field(description="Unique identifier for the task")
    title: str = Field(description="Title of the task")
    description: str = Field(description="Detailed description of the task")
    status: str = Field(description="Current status of the task")
    created_at: datetime = Field(description="Timestamp when the task was created")
    start_date: datetime = Field(description="Start date of the task")
    due_date: Optional[datetime] = Field(description="Due date for the task")


class TaskSubmitRequest(SQLModel):
    result: str = Field(description="Result or outcome of the task submitted by student")


class TaskRejectRequest(SQLModel):
    rejection_comment: str = Field(description="Comment from teacher explaining why task was rejected")
