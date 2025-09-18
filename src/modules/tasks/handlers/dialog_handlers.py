"""Handlers for tasks module using aiogram_dialog."""

import datetime
import os
from typing import Any

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from loguru import logger
from sqlalchemy import func, select, insert, update, text

from src.modules.tasks.states import TasksSG
from src.modules.shared.messages import StudentMessages
from src.modules.tasks import keyboard as tasks_keyboard
from src.modules.client import keyboard as client_keyboard
from src.storages.sql.dependencies import database
from src.storages.sql.models import TaskModel, tasks_table


def is_any_task(user_id: int) -> bool:
    """Check if user has any tasks for today."""
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


async def on_submit_tasks_clicked(
    callback: CallbackQuery, 
    widget, 
    dialog_manager: DialogManager
):
    """Handler for submit tasks button."""
    if is_any_task(callback.from_user.id):
        await callback.answer("Задания уже сегодня добавлялись!")
    else:
        await dialog_manager.switch_to(TasksSG.submit_task_first)


async def on_close_tasks_clicked(
    callback: CallbackQuery, 
    widget, 
    dialog_manager: DialogManager
):
    """Handler for close tasks button."""
    if is_any_task(callback.from_user.id):
        await dialog_manager.switch_to(TasksSG.close_tasks_confirm)
    else:
        await callback.answer(StudentMessages.TASKS_NOT_SET)


async def process_first_task(
    message: Message,
    widget,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Process first task input."""
    dialog_manager.dialog_data["task_one"] = text
    await dialog_manager.switch_to(TasksSG.submit_task_second)


async def process_second_task(
    message: Message,
    widget,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Process second task input and save both tasks."""
    task_one = dialog_manager.dialog_data.get("task_one", "")
    task_two = text
    
    now = datetime.datetime.utcnow()
    
    # Save tasks to database
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
    
    # Notify teacher
    teacher_tasks_id = os.getenv("TEACHER_TASKS_ID")
    if teacher_tasks_id:
        bot = dialog_manager.middleware_data.get("bot")
        if bot:
            await bot.send_message(
                teacher_tasks_id,
                f"<b>ID</b>: {request_id}\n(1) {task_one}\n(2) {task_two}",
                reply_markup=tasks_keyboard.keyboard_process_submit_task_teacher(),
            )
    else:
        logger.warning("TEACHER_TASKS_ID не установлен в переменных окружения")
    
    await message.answer(
        StudentMessages.SUCESSFULLY_ADDED_TASKS.format(request_id=request_id),
    )
    
    # Return to main menu (close dialog)
    await dialog_manager.done()


async def confirm_close_tasks(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
) -> None:
    """Confirm closing current tasks."""
    if is_any_task(callback.from_user.id):
        await callback.message.answer(StudentMessages.INVITE_OPERATOR_FOR_APPROVE)
        
        teacher_tasks_id = os.getenv("TEACHER_TASKS_ID")
        if teacher_tasks_id:
            bot = dialog_manager.middleware_data.get("bot")
            if bot:
                await bot.send_message(
                    teacher_tasks_id,
                    StudentMessages.ASK_OPERATOR_TO_COME_FOR_APPROVE.format(
                        request_id=database.last_added_id(callback.from_user.id)
                    ),
                    reply_markup=tasks_keyboard.keyboard_process_end_of_session_teacher(),
                )
        else:
            logger.warning("TEACHER_TASKS_ID не установлен в переменных окружения")
            
        await dialog_manager.done()
    else:
        await callback.answer(StudentMessages.TASKS_NOT_SET)


async def on_end_current_task(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
) -> None:
    """Handler for ending current task."""
    await dialog_manager.switch_to(TasksSG.add_new_second_task)


async def process_new_second_task(
    message: Message,
    widget,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Process new second task after ending first one."""
    # Update tasks: move second to first, add new second
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
        .values(task_second=text)
    )
    
    await message.answer("Задание обновлено!")
    await dialog_manager.done()


async def on_continue_task(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
) -> None:
    """Handler for continue current task."""
    await dialog_manager.switch_to(TasksSG.continue_task_options)


async def add_time_to_task(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
    minutes: int,
) -> None:
    """Add specified minutes to current task."""
    database.execute(
        update(tasks_table)
        .where(tasks_table.c.idt == callback.from_user.id)
        .values(start_time=tasks_table.c.start_time + text(f"INTERVAL '{minutes} minutes'"))
    )
    
    await callback.answer("Готово")
    await callback.message.answer(f"Добавлено {minutes} минут к заданию")
    await dialog_manager.done()


async def add_10_minutes(callback: CallbackQuery, widget, dialog_manager: DialogManager):
    """Add 10 minutes to current task."""
    await add_time_to_task(callback, widget, dialog_manager, 10)


async def add_15_minutes(callback: CallbackQuery, widget, dialog_manager: DialogManager):
    """Add 15 minutes to current task."""
    await add_time_to_task(callback, widget, dialog_manager, 15)


async def add_30_minutes(callback: CallbackQuery, widget, dialog_manager: DialogManager):
    """Add 30 minutes to current task."""
    await add_time_to_task(callback, widget, dialog_manager, 30)
