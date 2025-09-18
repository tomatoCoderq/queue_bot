import os
import datetime
from pyexpat.errors import messages

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command

from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter

from sqlalchemy import select, update

from src.storages.sql.dependencies import database
from src.storages.sql.models import TaskModel, tasks_table
from src.modules.shared.callbacks import CallbackDataKeys
# from main import dp
# from app.handlers.teacher import create_idt_name_map
from src.modules.shared.filters import IsStudent
from src.modules.shared.messages import StudentMessages


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
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.id == int(query_id))
            .where(tasks_table.c.status == 0)
            .values(status=1)
        )
        await callback.answer("Задачи приняты!")

    elif callback.data == CallbackDataKeys.reject_task:
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.id == int(query_id))
            .where(tasks_table.c.status == 0)
            .values(status=2)
        )
        client_task = database.fetch_one(
            select(tasks_table).where(tasks_table.c.id == int(query_id)),
            model=TaskModel,
        )

        if client_task:
            await bot.send_message(
                client_task.idt,
                "<b>Ваши задания были отклонены!</b> Пожалуйста, перепишите их и снова отправьте!",
                parse_mode=ParseMode.HTML,
            )

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
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.id == int(query_id))
            .values(status=3)
        )

    elif F.data == CallbackDataKeys.reject_end_of_session:
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.id == int(query_id))
            .values(status=4)
        )
        # client_id = database.fetchall("SELECT idt from tasks where id=?", (query_id,))

    await callback.answer("Задания на сегодня закрыты!")
    await callback.message.delete()

    client_task = database.fetch_one(
        select(tasks_table).where(tasks_table.c.id == int(query_id)),
        model=TaskModel,
    )
    if client_task:
        await bot.send_message(client_task.idt, "Ваша задачи на сегодня закрыты!")

    await state.clear()

    # Go to state with task given and submit button
