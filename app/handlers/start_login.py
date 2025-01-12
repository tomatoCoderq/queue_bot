import sqlite3

from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import BaseFilter
from utilits import keyboards
from aiogram import Bot, types, Dispatcher, Router
from loguru import logger

conn = sqlite3.connect("database/db.db")
cursor = conn.cursor()

router = Router()


class IsRegistered(BaseFilter):
    async def __call__(self, message: types.Message):
        ids = [x[0] for x in cursor.execute("SELECT idt FROM users").fetchall()]
        print(message.from_user.id, ids)
        return message.from_user.id in ids


@router.message(Command('start'), IsRegistered())
async def start_logging(message: types.Message, bot: Bot):
    ids = [x[0] for x in cursor.execute("SELECT idt FROM users").fetchall()]
    roles = [x[0] for x in cursor.execute("SELECT role FROM users").fetchall()]
    ids_roles_dict = {ids[i]: roles[i] for i in range(len(ids))}

    # Registration of student
    if message.from_user.id in ids:
        if ids_roles_dict[message.from_user.id] == "student":
            await bot.send_message(chat_id=message.from_user.id, text="С возвращением, <b>Ученик!</b>",
                                   reply_markup=keyboards.keyboard_main_student(), parse_mode=ParseMode.HTML)
            logger.info(f"{message.from_user.username} signed in as student")

        if ids_roles_dict[message.from_user.id] == "teacher":
            await bot.send_message(chat_id=message.from_user.id, text="С возвращением, <b>Преподаватель!</b>",
                                   reply_markup=keyboards.keyboard_main_teacher(), parse_mode=ParseMode.HTML)
            logger.info(f"{message.from_user.username} signed in as TEACHER")

        # if dict[message.from_user.id] == "parent":
        #     await bot.send_message(chat_id=message.from_user.id, text="С возвращением, <b>Родитель</b>",
        #                            reply_markup=keyboards.KeyboardM(), parse_mode=ParseMode.HTML)
        #     logger.info(f"Signed in {message.from_user.username} as PARENT")
