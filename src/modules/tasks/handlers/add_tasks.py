import asyncio
import datetime
import os
import time

import aioschedule
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from src.modules.client import keyboard as client_keyboard
from src.modules.tasks import keyboard as tasks_keyboard
from src.modules.shared.callbacks import CallbackDataKeys
from src.modules.shared.messages import StudentMessages, TeacherMessages
from sqlalchemy import and_, func, insert, select, update, text

from src.storages.sql.dependencies import database
from src.storages.sql.models import TaskModel, tasks_table

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
    tasks = database.fetch_all(
        select(tasks_table)
        .where(tasks_table.c.idt == user_id)
        .where(tasks_table.c.status.in_([1, 5]))
        .where(func.date(tasks_table.c.start_time) == func.current_date())
        .order_by(tasks_table.c.id),
        model=TaskModel,
    )

    if not tasks:
        return StudentMessages.NO_TASKS

    current = tasks[-1]
    return f"<b>Задачи на сегодня:</b>\n(1) {current.task_first}\n(2) {current.task_second}"


def is_any_task(user_id):
    tasks = database.fetch_all(
        select(tasks_table)
        .where(tasks_table.c.idt == user_id)
        .where(tasks_table.c.status.in_([1, 5]))
        .where(func.date(tasks_table.c.start_time) == func.current_date())
        .order_by(tasks_table.c.id),
        model=TaskModel,
    )

    if not tasks:
        return False

    latest = tasks[-1]
    start_date = str(latest.start_time)[:10]
    return start_date == datetime.datetime.now().strftime("%Y-%m-%d")

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

    database.execute(
        insert(tasks_table).values(
            idt=message.from_user.id,
            task_first=task_one,
            task_second=task_two,
            start_time=now.strftime("%Y-%m-%d %H:%M:%S"),
            status=0,
            shift=0,
        )
    )

    request_id = database.last_added_id(message.from_user.id)

    teacher_tasks_id = os.getenv("TEACHER_TASKS_ID")
    if teacher_tasks_id:
        await bot.send_message(
            teacher_tasks_id,
            f"<b>ID</b>: {request_id}\n(1) {task_one}\n(2) {task_two}",
            reply_markup=tasks_keyboard.keyboard_process_submit_task_teacher(),
        )
    else:
        logger.warning("TEACHER_TASKS_ID не установлен в переменных окружения")

    await message.answer(
        StudentMessages.SUCESSFULLY_ADDED_TASKS.format(request_id=request_id),
        reply_markup=client_keyboard.keyboard_main_student(),
    )
    await state.clear()


@router.callback_query(F.data == CallbackDataKeys.close_tasks)
async def close_tasks(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    if is_any_task(callback.from_user.id):
        await callback.message.answer(StudentMessages.INVITE_OPERATOR_FOR_APPROVE)
        teacher_tasks_id = os.getenv("TEACHER_TASKS_ID")
        if teacher_tasks_id:
            await bot.send_message(
                teacher_tasks_id,
                StudentMessages.ASK_OPERATOR_TO_COME_FOR_APPROVE.format(
                    request_id=database.last_added_id(callback.from_user.id)
                ),
                reply_markup=tasks_keyboard.keyboard_process_end_of_session_teacher(),
            )
        else:
            logger.warning("TEACHER_TASKS_ID не установлен в переменных окружения")
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

    database.execute(
        update(tasks_table)
        .where(tasks_table.c.idt == message.from_user.id)
        .where(tasks_table.c.status.in_([1, 5]))
        .values(task_first=tasks_table.c.task_second)
    )
    database.execute(
        update(tasks_table)
        .where(tasks_table.c.idt == message.from_user.id)
        .where(tasks_table.c.status.in_([1, 5]))
        .values(task_second=message.text)
    )

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
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.idt == callback.from_user.id)
            .values(start_time=tasks_table.c.start_time + text("INTERVAL '10 minutes'"))
        )

        await callback.answer("Готово")
        await callback.message.answer("Выбирайте", reply_markup=client_keyboard.keyboard_main_student())

    elif callback.data == "15":
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.idt == callback.from_user.id)
            .values(start_time=tasks_table.c.start_time + text("INTERVAL '15 minutes'"))
        )
        await callback.answer("Готово")
        await callback.message.answer("Выбирайте", reply_markup=client_keyboard.keyboard_main_student())

    elif callback.data == "30":
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.idt == callback.from_user.id)
            .values(start_time=tasks_table.c.start_time + text("INTERVAL '30 minutes'"))
        )
        await callback.answer("Готово")
        await callback.message.answer("Выбирайте", reply_markup=client_keyboard.keyboard_main_student())

    database.execute(
        update(tasks_table)
        .where(tasks_table.c.idt == callback.from_user.id)
        .values(shift=(func.coalesce(tasks_table.c.shift, 0) + 1))
    )
    await callback.message.delete()

    teacher_tasks_id = os.getenv("TEACHER_TASKS_ID")
    if teacher_tasks_id:
        await bot.send_message(teacher_tasks_id, f"Пользователь {callback.from_user.username} сдвинул задание на {callback.data} минут")
    else:
        logger.warning("TEACHER_TASKS_ID не установлен в переменных окружения")


async def noon_print(bot: Bot):
    #TODO: check that passed only one hour
    #and start_time=DATETIME(start_time, '+20 minutes')
    # print(database.fetchall("SELECT strftime('%s', 'now')"))

    time.tzset()
    active_tasks = database.fetch_all(
        select(tasks_table).where(tasks_table.c.status.in_([1, 5])),
        model=TaskModel,
    )

    current_time = datetime.datetime.now()
    current_date = current_time.date()
    users_to_notify: set[int] = set()

    for task in active_tasks:
        start_str = str(task.start_time)
        try:
            start_dt = (
                task.start_time
                if isinstance(task.start_time, datetime.datetime)
                else datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            )
        except ValueError:
            continue

        if start_dt.date() != current_date:
            continue

        if (current_time - start_dt).total_seconds() >= 3600:
            users_to_notify.add(task.idt)

    for user_id in users_to_notify:
        await bot.send_message(user_id, "Прошел один час, готовы ли задания",
                               reply_markup=client_keyboard.keyboard_end_of_hour_check_student())


async def scheduler(bot: Bot):
    # aioschedule.every(1).minutes.do(noon_print, bot)
    aioschedule.every(60).seconds.do(noon_print, bot)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

# cancel button

# write operator logic for the task in separate file
