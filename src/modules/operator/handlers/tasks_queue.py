# print all names and ask to write alias of client you want to see operations and current task

import asyncio
import os
import datetime
import time

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command
from sqlalchemy import select

from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter
import aioschedule

from src.storages.sql.dependencies import database
from src.storages.sql.models import StudentModel, students_table
from src.modules.shared.callbacks import CallbackDataKeys
# from main import dp
# from app.handlers.teacher import create_idt_name_map
from src.modules.shared.filters import IsStudent
from src.modules.shared.messages import StudentMessages

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.modules.tasks.handlers.add_tasks import is_any_task

scheduler = AsyncIOScheduler()


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
# 3 - Succesfully ended the day
# 4 - Haven't done the task in the end of the day
# 5 - Shifted (can be shown)

# class TasksSubmit(StatesGroup):
#     get_task_one = State()
#     get_task_two = State()


# class ShowClientCard(StatesGroup):
#     get_client_id = State()
#     further_actions = State()
#     get_changed_task = State()
#     set_tasks = State()
#     set_tasks_one = State()
#     set_tasks_two = State()


def map_names_and_idt() -> dict[str, tuple[str, str]]:
    records = database.fetch_all(
        select(students_table.c.idt, students_table.c.name, students_table.c.surname)
        .order_by(students_table.c.surname),
        model=StudentModel,
    )
    return {record.idt: (record.surname, record.name) for record in records}


def form_the_message_with_tasks_to_teacher():
    message_to_send = "Введите ID нужного пользователя:\n"
    names_ids = map_names_and_idt()

    for idt, name in names_ids.items():
        message_to_send += f"{name[0]} {name[1]} | {idt}\n"

    return message_to_send
#
#
# print(form_the_message_with_tasks_to_teacher("ds"))
#
#
# @router.callback_query(F.data.in_({CallbackDataKeys.client_tasks, CallbackDataKeys.back_to_tasks_teacher}))
# async def client_tasks(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(form_the_message_with_tasks_to_teacher(),
#                                      reply_markup=keyboards.keyboard_back_to_main_teacher())
#
#     await state.set_state(ShowClientCard.get_client_id)
#     await state.update_data(prev_msg_id=callback.message.message_id)
#     # Go to state with task given and submit button
#
#
# @router.message(F.text, ShowClientCard.get_client_id)
# async def task_card(message: types.Message, state: FSMContext, bot: Bot):
#     # Need to show card with two current task, end of beginning, whether session is closed and button
#     # with ability to change task and/or reject current task
#
#     data = await state.get_data()
#
#     query = database.fetchall_multiple(f"SELECT * from tasks where idt={message.text} "
#                                        f"and (status = 1 or status = 5)")
#
#     if len(query) != 0:
#         query = query[-1]
#
#         await bot.delete_message(message.from_user.id, data['prev_msg_id'])
#         await message.delete()
#         await message.answer(
#             f"{query[2]}\n{query[3]}\nНачало: {datetime.datetime.strptime(query[4], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=180)}\nПереносы: {query[6]}\n",
#             reply_markup=keyboards.keyboard_task_card_teacher())
#
#         # print(datetime.datetime.strptime(query[4], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=180))
#
#         await state.set_state(ShowClientCard.further_actions)
#         # await state.update_data(idt=message.text)
#
#     else:
#         await bot.delete_message(message.from_user.id, data['prev_msg_id'])
#         await message.delete()
#         await message.answer(f"Заданий нет!",
#                              reply_markup=keyboards.keyboard_task_card_teacher())
#
#     await state.update_data(idt=message.text)
#
#         # await state.set_state(ShowClientCard.further_actions)
#         # await state.update_data(idt=message.text)
#
#
# @router.callback_query(F.data == CallbackDataKeys.change_current_task)
# async def change_task_empty(callback: types.CallbackQuery, state: FSMContext):
#     await callback.answer("Это просто заглушка! Выбор ниже")
#
#
# @router.callback_query(F.data.in_({CallbackDataKeys.task_one, CallbackDataKeys.task_two}),
#                        ShowClientCard.further_actions)
# async def ask_new_tasks(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.answer("Напишите сообщение")
#     await callback.message.delete()
#
#     await state.set_state(ShowClientCard.get_changed_task)
#     if callback.data == CallbackDataKeys.task_one:
#         await state.update_data(task="task_one")
#
#     if callback.data == CallbackDataKeys.task_two:
#         await state.update_data(task="task_two")
#
#
# # @router.callback_query(F.data == "task_two", ShowClientCard.further_actions)
# # async def ask_new_tasks(callback: types.CallbackQuery, state: FSMContext):
# #     await callback.message.answer("Напишите сообщение")
# #     await callback.message.delete()
# #
# #     await state.set_state(ShowClientCard.get_changed_task)
# #     await state.update_data(task="task_two")
#
#
# @router.message(F.text, ShowClientCard.get_changed_task)
# async def get_changed_task(message: types.Message, state: FSMContext, bot: Bot):
#     data = await state.get_data()
#
#     # print(database.last_added_id(data['idt']))
#
#     if data['task'] == "task_one":
#         database.execute(
#             f"UPDATE tasks SET task_first=? where id={database.last_added_id(data['idt'])} and (status = 1 or status = 5)",
#             (message.text,))
#         await message.answer("Задание 1 изменено", reply_markup=keyboards.keyboard_main_teacher())
#         await bot.send_message(data['idt'], "Задача 1 была изменена оператором")
#
#     elif data['task'] == "task_two":
#         database.execute(
#             f"UPDATE tasks SET task_second=? where id={database.last_added_id(data['idt'])} and (status = 1 or status = 5)",
#             (message.text,))
#         await message.answer("Задание 2 изменено", reply_markup=keyboards.keyboard_main_teacher())
#         await bot.send_message(data['idt'], "Задача 2 была изменена оператором")
#
#     await message.delete()
#     await state.clear()
#
#
# @router.callback_query(F.data == "add_tasks_to_student")
# async def set_tasks_one(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.answer("Напишите задачу один")
#     await callback.message.delete()
#
#     await state.set_state(ShowClientCard.set_tasks_one)
#
# @router.message(F.text, ShowClientCard.set_tasks_one)
# async def set_tasks_two(message: types.Message, state: FSMContext):
#     await message.answer("Напишите задачу два")
#     await message.delete()
#
#     await state.set_state(ShowClientCard.set_tasks_two)
#     await state.update_data(task_one=message.text)
#     # await state.update_data(task_one=call.text)
#
#
# @router.message(F.text, ShowClientCard.set_tasks_two)
# async def set_tasks(message: types.Message, state: FSMContext, bot: Bot):
#     data = await state.get_data()
#     task_one = data['task_one']
#     task_two = message.text
#
#     # os.environ['TZ'] = 'Europe/Moscow'
#     # time.tzset()
#
#     now = datetime.datetime.utcnow()
#
#     print(now)
#
#     to_insert = [int(data['idt']),
#                  task_one,
#                  task_two,
#                  now.strftime("%Y-%m-%d %H:%M:%S"),
#                  1,
#                  0]
#
#     # TODO: class should throw error and handle here
#     # print(datetime.datetime.now(datetime.timezone("Europe/Moscow")))
#     database.execute("INSERT INTO tasks VALUES (NULL, ?, ?, ?, ?, ?, ?)", to_insert)
#
#     # await bot.send_message(os.getenv("TEACHER_TASKS_ID"),
#     #                        f"<b>ID</b>: {database.fetchall('select id from tasks order by id desc')[0]}\n"
#     #                        f"(1) {task_one}\n(2) {task_two}",
#     #                        reply_markup=keyboards.keyboard_process_submit_task_teacher())
#
#     request_id = database.fetchall("SELECT id FROM tasks WHERE idt=?", (data['idt'],))[-1]
#
#     await message.answer(StudentMessages.SUCESSFULLY_ADDED_TASKS.format(request_id=request_id),
#                          reply_markup=keyboards.keyboard_main_teacher())
#     await state.clear()
