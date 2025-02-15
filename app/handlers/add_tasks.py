import asyncio
import os
import datetime
import time
from datetime import tzinfo, timedelta

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command

from app.handlers.test_handlers import update
from app.utilits import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter
import aioschedule

from app.utilits.database import database
from app.utilits.keyboards import CallbackDataKeys
# from main import dp
from app.handlers.teacher import create_idt_name_map
from app.utilits.filters import IsStudent
from app.utilits.messages import StudentMessages, TeacherMessages

from apscheduler.schedulers.asyncio import AsyncIOScheduler

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

class TasksSubmit(StatesGroup):
    get_task_one = State()
    get_task_two = State()


class EndCurrentTask(StatesGroup):
    get_new_task = State()


def form_the_message_with_tasks(user_id):
    query = database.fetchall_multiple(f"SELECT * from tasks where idt=? and (status=1 or status=5) and SUBSTR(start_time, 1, 10)=DATE('now', 'utc')", (user_id, ))
    print(database.fetchall(f"Select * from tasks where SUBSTR(start_time, 1, 10)=DATE('now', 'utc') and (status=1 or status=5) and idt=?", (str(user_id), )))
    print("DATENOW", database.fetchall_multiple("SELECT DATE('now')"))

    print("from", query)

    if len(query) == 0:
        message_to_send = StudentMessages.NO_TASKS
        return message_to_send

    query = query[-1]

    message_to_send = f"<b>Задачи на сегодня:</b>\n(1) {query[2]}\n(2) {query[3]}"
    return message_to_send


def is_any_task(user_id):
    query = database.fetchall_multiple("SELECT * from tasks where idt=? and (status=1 or status=5) and SUBSTR(start_time, 1, 10)=DATE('now')", (user_id,))

    print(query)

    if len(query) == 0:
        return False

    query = query[-1]

    # I cut off hours:minutes:seconds, form date and compare with current date
    if (datetime.datetime.date(datetime.datetime.strptime(query[4][:10], "%Y-%m-%d"))
            == datetime.datetime.date(datetime.datetime.now())):
        return True

    return False

    # Check whether user with given id has any task with today's date and code 1 or 5


# print(form_the_message_with_tasks("6647065320"))/


@router.callback_query(F.data == CallbackDataKeys.tasks)
async def tasks(callback: types.CallbackQuery):
    # Here will be tasks
    print(callback.from_user.id)
    await callback.message.edit_text(form_the_message_with_tasks(callback.from_user.id),
                                     reply_markup=keyboards.keyboard_submit_tasks_student())

    # Go to state with task given and submit button


@router.callback_query(F.data == CallbackDataKeys.submit_tasks)
async def submit_tasks(callback: types.CallbackQuery, state: FSMContext):
    # Need to check whether task was recently uploaded. If it was sent to rewriting then allow to rewrite
    # else send reject message

    if is_any_task(callback.from_user.id):
        await callback.answer("Задания уже сегодня добавлялись!")

    else:
        await callback.message.answer(StudentMessages.WRITE_FIRST_TASK_TO_SUBMIT)
        await state.set_state(TasksSubmit.get_task_one)


@router.message(F.text, TasksSubmit.get_task_one)
async def get_task_one(message: types.Message, state: FSMContext):
    # task_one_to_add = message.text
    # get first task and set value to second
    await message.answer(StudentMessages.WRITE_SECOND_TASK_TO_SUBMIT)
    await state.set_state(TasksSubmit.get_task_two)
    await state.update_data(task_one=message.text)

# print(datetime.datetime.utcnow())

@router.message(F.text, TasksSubmit.get_task_two)
async def get_task_two(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    task_one = data['task_one']
    task_two = message.text

    # os.environ['TZ'] = 'Europe/Moscow'
    # time.tzset()

    now = datetime.datetime.utcnow()

    print(now)

    to_insert = [message.from_user.id,
                 task_one,
                 task_two,
                 now.strftime("%Y-%m-%d %H:%M:%S"),
                 0,
                 0]

    # TODO: class should throw error and handle here
    # print(datetime.datetime.now(datetime.timezone("Europe/Moscow")))
    database.execute("INSERT INTO tasks VALUES (NULL, ?, ?, ?, ?, ?, ?)", to_insert)

    await bot.send_message(os.getenv("TEACHER_TASKS_ID"),
                           f"<b>ID</b>: {database.fetchall('select id from tasks order by id desc')[0]}\n"
                           f"(1) {task_one}\n(2) {task_two}",
                           reply_markup=keyboards.keyboard_process_submit_task_teacher())

    request_id = database.fetchall("SELECT id FROM tasks WHERE idt=?", (message.from_user.id, ))[-1]

    await message.answer(StudentMessages.SUCESSFULLY_ADDED_TASKS.format(request_id=request_id), reply_markup=keyboards.keyboard_main_student())
    await state.clear()


@router.callback_query(F.data == CallbackDataKeys.close_tasks)
async def close_tasks(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    if is_any_task(callback.from_user.id):
        await callback.message.answer(StudentMessages.INVITE_OPERATOR_FOR_APPROVE)
        await bot.send_message(os.getenv("TEACHER_TASKS_ID"), f"Подойдите на апрув запроса с\nID: {database.last_added_id(callback.from_user.id)}",
                               reply_markup=keyboards.keyboard_process_end_of_session_teacher())
    else:
        await callback.answer(StudentMessages.TASKS_NOT_SET)


@router.callback_query(F.data == CallbackDataKeys.end_current_task)
async def end_current_task_ask_new_task(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    # Ask operator to come. He can approve the work or ask to add minutes to continue
    # End current task: take second task, add as new element, ask to write second new task
    # Or previous second task can be rewritten if it changed
    # await bot.send_message(os.getenv("TEACHER_TASKS_ID"), f"Подойдите на апрув конца задания\nID: {database.last_added_id()}",
    #                        reply_markup=keyboards.keyboard_process_end_of_session_teacher())
    #
    # query = database.fetchall_multiple("SELECT * from tasks where idt=? and (status=1 or status=5)", (user_id,))

    await callback.message.answer("OK, пиши новое задание номер два")

    await state.set_state(EndCurrentTask.get_new_task)


@router.message(F.text, EndCurrentTask.get_new_task)
async def end_current_task(message: types.Message, state: FSMContext, bot: Bot):
    # query = database.fetchall_multiple("SELECT * from tasks where idt=? and (status=1 or status=5)", (message.from_user.id, ))

    database.execute("update tasks set task_first=task_second where idt=? and (status=1 or status=5)",
                     (message.from_user.id,))
    database.execute("update tasks set task_second=? where idt=? and (status=1 or status=5)",
                     (message.text, message.from_user.id))

    await state.clear()


@router.callback_query(F.data.in_({CallbackDataKeys.continue_current_task,
                                   CallbackDataKeys.add_10_minutes,
                                   CallbackDataKeys.add_15_minutes,
                                   CallbackDataKeys.add_30_minutes}))
async def continue_current_task(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    # Continue: add to database time 10, 15, or 30 minutes to initial time

    if callback.data == CallbackDataKeys.continue_current_task:
        await callback.answer("А это просто заглушка. Выбирайте ниже!")

    elif callback.data == "10":
        database.execute("UPDATE tasks SET start_time = DATETIME(start_time, '+10 minutes') where idt=?", (callback.from_user.id, ))

        await callback.answer("Готово")
        await callback.message.answer("Выбирайте", reply_markup=keyboards.keyboard_main_student())

    elif callback.data == "15":
        database.execute("UPDATE tasks SET start_time = DATETIME(start_time, '+15 minutes') where idt=?", (callback.from_user.id, ))
        await callback.answer("Готово")
        await callback.message.answer("Выбирайте", reply_markup=keyboards.keyboard_main_student())

    elif callback.data == "30":
        database.execute("UPDATE tasks SET start_time = DATETIME(start_time, '+30 minutes') where idt=?", (callback.from_user.id, ))
        await callback.answer("Готово")
        await callback.message.answer("Выбирайте", reply_markup=keyboards.keyboard_main_student())

    database.execute("UPDATE tasks SET shift = shift + 1 where idt=?", (callback.from_user.id,))
    await callback.message.delete()

    await bot.send_message(os.getenv("TEACHER_TASKS_ID"), f"Пользователь {callback.from_user.username} сдвинул задание на {callback.data} минут")


async def noon_print(bot: Bot):
    #TODO: check that passed only one hour
    #and start_time=DATETIME(start_time, '+20 minutes')
    # print(database.fetchall("SELECT strftime('%s', 'now')"))

    time.tzset()
    user_ids = database.fetchall("SELECT idt FROM tasks WHERE (status = 1 or status = 5) "
                                 "and DATE(start_time) = DATE('now') "
                                 "AND (strftime('%s', 'now') - strftime('%s', start_time)) >= 3600;")
    # print(database.fetchall("SELECT strftime('%s', 'now')"))
    # print(database.fetchall("SELECT strftime('%s', 'now', 'localtime')"))
    # print(database.fetchall("SELECT strftime('%s', start_time) from tasks")[-1])
    # print( database.fetchall("select datetime('now') from tasks where status = 1 or status = 5"))
    # print(database.fetchall("select DATETIME(start_time, '+1 minutes') from tasks where (status = 1 or status = 5)"))
    # print(database.fetchall("SELECT idt FROM tasks WHERE (status = 1 or status = 5) and DATE(start_time) = DATE('now') AND (strftime('%s', 'now') - strftime('%s', start_time)) >= 1 * 3600;"))

    print(user_ids)
    #
    for user_id in user_ids:
        await bot.send_message(user_id, "Прошел один час, готовы ли задания",
                               reply_markup=keyboards.keyboard_end_of_hour_check_student())


async def scheduler(bot: Bot):
    # aioschedule.every(1).minutes.do(noon_print, bot)
    aioschedule.every(60).seconds.do(noon_print, bot)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

# cancel button

# write operator logic for the task in separate file
