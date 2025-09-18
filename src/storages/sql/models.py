"""Pydantic models describing database records."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)


metadata = MetaData()


users_table = Table(
    "users",
    metadata,
    Column("idt", BigInteger, primary_key=True),
    Column("user", String, nullable=False),
    Column("role", String, nullable=True),
)


students_table = Table(
    "students",
    metadata,
    Column("idt", BigInteger, primary_key=True),
    Column("name", String, nullable=False),
    Column("surname", String, nullable=False),
)


requests_queue_table = Table(
    "requests_queue",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("idt", BigInteger, nullable=False),
    Column("urgency", Integer, nullable=False),
    Column("type", String, nullable=False),
    Column("status", Integer, nullable=False, default=0),
    Column("send_date", String, nullable=True),
    Column("comment", Text, nullable=True),
    Column("amount", Integer, nullable=True),
    Column("file_name", String, nullable=True),
    Column("value", Integer, nullable=True),
    Column("proceeed", Integer, nullable=False, default=0),
    Column("params", String, nullable=True),
    Column("owner", BigInteger, nullable=True),
    Column("close_time", String, nullable=True),
)


tasks_table = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("idt", BigInteger, nullable=False),
    Column("task_first", Text, nullable=False),
    Column("task_second", Text, nullable=False),
    Column("start_time", String, nullable=False),
    Column("status", Integer, nullable=False, default=0),
    Column("shift", Integer, nullable=True),
    Column("close_time", String, nullable=True),
)


penalty_table = Table(
    "penalty",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("idt", BigInteger, nullable=False),
    Column("reason", Text, nullable=False),
)


details_table = Table(
    "details",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("price", Integer, nullable=False),
    Column("owner", BigInteger, nullable=True),
)


detail_aliases_table = Table(
    "detail_aliases",
    metadata,
    Column("name", String, primary_key=True),
    Column("alias", String, nullable=False),
)


class DBModel(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class UserModel(DBModel):
    idt: int
    user: str
    role: Optional[str] = None


class StudentModel(DBModel):
    idt: int
    name: str
    surname: str


class PenaltyModel(DBModel):
    id: int
    idt: int
    reason: str


class TaskModel(DBModel):
    id: int
    idt: int
    task_first: str
    task_second: str
    start_time: datetime | str
    status: int
    shift: Optional[int] = None
    close_time: Optional[datetime | str] = None


class RequestModel(DBModel):
    id: int
    idt: int
    urgency: int
    type: str
    status: int
    send_date: datetime | str | None = None
    comment: Optional[str] = None
    amount: Optional[int] = None
    file_name: Optional[str] = None
    value: Optional[int] = None
    proceeed: Optional[int] = None
    params: Optional[str] = None
    owner: Optional[int] = None
    close_time: Optional[datetime | str] = None


class DetailModel(DBModel):
    id: int
    name: str
    price: float
    owner: Optional[int] = None


class DetailAliasModel(DBModel):
    name: str
    alias: str
