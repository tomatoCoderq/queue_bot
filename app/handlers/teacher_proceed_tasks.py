import os
import datetime
from pyexpat.errors import messages

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
from app.utilits.filters import IsStudent
from app.utilits.messages import StudentMessages


class UserTask:
    def __init__(self, idt, task_first, task_second):
        self.idt = idt
        self.task_first = task_first
        self.task_second = task_second


router = Router()
dp = Dispatcher()


# Codes
# 0 - Inserted but not proceed (cannot be shown)
# 1 - Proceed, Approved (can be shown)
# 2 - Proceed, Rejected (cannot be shown)
# 3 - Successfully ended the day
# 4 - Haven't done the task in the end of the day
# 5 - Shifted (can be shown)

class TasksSubmit(StatesGroup):
    get_task_one = State()
    get_task_two = State()


@router.callback_query(F.data.in_({CallbackDataKeys.accept_task, CallbackDataKeys.reject_task}))
async def proceeding_tasks(callback: types.CallbackQuery, state: FSMContext, bot:Bot):
    query_id = callback.message.text.split()[1]
    print("query", query_id)

    if callback.data == CallbackDataKeys.accept_task:
        database.execute("UPDATE tasks SET status=1 WHERE id=? and status=0", (query_id,))
        await callback.answer("Задачи приняты!")

    elif callback.data == CallbackDataKeys.reject_task:
        database.execute("UPDATE tasks SET status=2 WHERE id=? and status=0", (query_id,))
        client_id = database.fetchall("SELECT idt from tasks where id=?", (query_id,))

        print(client_id)

        await bot.send_message(client_id[-1], "<b>Ваши задания были отклонены!</b> Пожалуйста, перепишите их и снова отправьте!")

        await callback.answer("Задачи отклонены!")

    await callback.message.delete()
    await state.clear()

    # Go to state with task given and submit button


@router.callback_query(F.data.in_({CallbackDataKeys.accept_end_of_session, CallbackDataKeys.reject_end_of_session}))
async def proceeding_end_of_session(callback: types.CallbackQuery, state: FSMContext, bot:Bot):
    query_id = callback.message.text.split()[-1]
    print(query_id)

    # TODO: fix bug with both entries
    if F.data == CallbackDataKeys.accept_end_of_session:
        database.execute("UPDATE tasks SET status=3 WHERE id=?", (query_id,))

    elif F.data == CallbackDataKeys.reject_end_of_session:
        database.execute("UPDATE tasks SET status=4 WHERE id=?", (query_id,))
        # client_id = database.fetchall("SELECT idt from tasks where id=?", (query_id,))

    await callback.answer("Задания на сегодня закрыты!")
    await callback.message.delete()

    idt = database.fetchall("select idt from tasks where id=?", (query_id, ))
    await bot.send_message(idt[-1], "Ваша задачи на сегодня закрыты!")

    await state.clear()

    # Go to state with task given and submit button
