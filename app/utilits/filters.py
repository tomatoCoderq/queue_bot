import os
import datetime

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command

from app.utilits import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter

from app.utilits.database import database
from app.utilits.keyboards import CallbackDataKeys
# from main import dp
from app.handlers.teacher import create_idt_name_map



class IsStudent(BaseFilter):
    async def __call__(self, message: types.Message):
        # Take only possible role satisfying query
        role = database.fetchall(f"SELECT role FROM users WHERE idt=?", (message.from_user.id,))[0]
        return role == "student"


class IsTeacher(BaseFilter):
    async def __call__(self, message: types.Message):
        # Take only possible role satisfying query
        role = database.fetchall(f"SELECT role FROM users WHERE idt=?", (message.from_user.id,))[0]
        return role == "teacher"


class IsRegistered(BaseFilter):
    async def __call__(self, message: types.Message):
        # print(f" here {database.database.fetchall('SELECT idt FROM users')}")
        ids = database.fetchall("SELECT idt FROM users")
        # ids = [x[0] for x in cursor.execute("SELECT idt FROM users").fetchall()]
        print(message.from_user.id, ids)
        return message.from_user.id in ids


class IsNotRegistered(BaseFilter):
    async def __call__(self, message: types.Message):
        ids = database.fetchall("SELECT idt FROM users")
        # ids = [x[0] for x in cursor.execute("SELECT idt FROM users").fetchall()]
        print(message.from_user.id, ids)
        return message.from_user.id not in ids
