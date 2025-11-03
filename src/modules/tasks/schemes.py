from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import model_validator
from sqlmodel import SQLModel, Field 



class TaskCreateRequest(SQLModel):
    title: str = Field(description="Title of the task")
    description: Optional[str] = Field(description="Detailed description of the task")
    start_date: str = Field(default_factory=datetime.utcnow,description="Start date for the task in YYYY-MM-DD format")
    due_date: Optional[str] = Field(default=None, description="Due date for the task in YYYY-MM-DD format")
    
    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date is None or self.due_date is None:
            return self
        
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        due = datetime.strptime(self.due_date, "%Y-%m-%d") # type: ignore

        if start >= due:
            raise ValueError("start_date must be earlier than due_date")
        return self

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
    description: str = Field(description="Detailed description of the task")
    status: str = Field(description="Current status of the task")
    created_at: datetime = Field(description="Timestamp when the task was created")
    start_date: datetime = Field(description="Start date of the task")
    due_date: Optional[datetime] = Field(description="Due date for the task")
    student_id: Optional[UUID] = Field(description="ID of the student the task is assigned to")
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