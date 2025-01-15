import sqlite3
import os
import datetime
from pyexpat.errors import messages

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from aiogram.filters import StateFilter, Command
from utilits import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter
from app.handlers.teacher import status_int_to_str

router = Router()

conn = sqlite3.connect("database/db.db")
cursor = conn.cursor()


def generate_message_to_send(students_messages) -> str:
    message_to_send = [
        (f"<b>ID</b>: {students_messages[i][0]}\n"
         f"<b>Статус</b>: {status_int_to_str(students_messages[i][4])}\n---\n") for i in range(len(students_messages))]

    s = 'Очередь заданий: \n---\n'
    if len(message_to_send) == 0:
        s += "Очередь заданий пуста!"
    else:
        for a in message_to_send:
            s += a
    return s


@router.callback_query(F.data == "student_requests")
async def student_requests(callback: types.CallbackQuery):
    students_messages = [x for x in
                         cursor.execute(f"SELECT * FROM requests_queue "
                                        f"WHERE proceeed!=2 "
                                        f"AND idt={callback.from_user.id}").fetchall()]
    await callback.message.edit_text(generate_message_to_send(students_messages),
                                     reply_markup=keyboards.keyboard_back_to_main_student(), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data == "back_to_main_student")
async def student_requests(callback: types.CallbackQuery):
    await callback.message.edit_text("Выбирайте, <b>Клиент!</b>",
                                     reply_markup=keyboards.keyboard_main_student(), parse_mode=ParseMode.HTML)
    await callback.answer()
