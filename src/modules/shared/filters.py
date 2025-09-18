from aiogram import types
from aiogram.filters import BaseFilter
from sqlalchemy import select

from src.storages.sql.dependencies import database
from src.storages.sql.models import UserModel, users_table


class IsStudent(BaseFilter):
    async def __call__(self, message: types.Message):
        # Take only possible role satisfying query
        user = database.fetch_one(
            select(users_table).where(users_table.c.idt == message.from_user.id),
            model=UserModel,
        )
        return user is not None and user.role == "student"


class IsTeacher(BaseFilter):
    async def __call__(self, message: types.Message):
        # Take only possible role satisfying query
        user = database.fetch_one(
            select(users_table).where(users_table.c.idt == message.from_user.id),
            model=UserModel,
        )
        return user is not None and user.role == "teacher"


class IsRegistered(BaseFilter):
    async def __call__(self, message: types.Message):
        # print(f" here {database.database.fetchall('SELECT idt FROM users')}")
        ids = set(database.fetch_column(select(users_table.c.idt)))
        print("IDSS", ids)

        # ids = [x[0] for x in cursor.execute("SELECT idt FROM users").fetchall()]
        return message.from_user.id in ids


class IsNotRegistered(BaseFilter):
    async def __call__(self, message: types.Message):
        ids = set(database.fetch_column(select(users_table.c.idt)))
        print("IDSS", ids)
        # ids = [x[0] for x in cursor.execute("SELECT idt FROM users").fetchall()]
        return message.from_user.id not in ids
