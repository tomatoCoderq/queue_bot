"""Handlers for operator tasks module using aiogram_dialog."""

import datetime
from typing import Any

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from loguru import logger
from sqlalchemy import select, update, func

from src.modules.operator.states import OperatorTasksSG
from src.storages.sql.dependencies import database
from src.storages.sql.models import TaskModel, tasks_table


async def on_client_tasks_clicked(
    callback: CallbackQuery, 
    widget, 
    dialog_manager: DialogManager
):
    """Handler for client tasks button."""
    await dialog_manager.switch_to(OperatorTasksSG.client_selection)


async def on_history_clicked(
    callback: CallbackQuery, 
    widget, 
    dialog_manager: DialogManager
):
    """Handler for history button."""
    await callback.answer("История заданий - в разработке")


async def on_get_xlsx_clicked(
    callback: CallbackQuery, 
    widget, 
    dialog_manager: DialogManager
):
    """Handler for get xlsx button."""
    await callback.answer("Экспорт в Excel - в разработке")


async def on_client_selected(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
    item_id: str,
):
    """Handler for client selection."""
    dialog_manager.dialog_data["selected_client_id"] = int(item_id)
    await dialog_manager.switch_to(OperatorTasksSG.client_task_card)


async def on_change_task_one(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
):
    """Handler for changing task one."""
    dialog_manager.dialog_data["changing_task"] = "1"
    await dialog_manager.switch_to(OperatorTasksSG.change_task_one)


async def on_change_task_two(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
):
    """Handler for changing task two."""
    dialog_manager.dialog_data["changing_task"] = "2"
    await dialog_manager.switch_to(OperatorTasksSG.change_task_two)


async def process_task_change(
    message: Message,
    widget,
    dialog_manager: DialogManager,
    text: str,
):
    """Process task change."""
    client_id = dialog_manager.dialog_data.get("selected_client_id")
    changing_task = dialog_manager.dialog_data.get("changing_task", "1")
    
    if not client_id:
        await message.answer("Ошибка: студент не выбран")
        return
    
    # Update the appropriate task
    if changing_task == "1":
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.idt == client_id)
            .where(tasks_table.c.status.in_([1, 5]))
            .where(func.date(tasks_table.c.start_time) == func.current_date())
            .values(task_first=text)
        )
    else:
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.idt == client_id)
            .where(tasks_table.c.status.in_([1, 5]))
            .where(func.date(tasks_table.c.start_time) == func.current_date())
            .values(task_second=text)
        )
    
    await message.answer(f"Задание {changing_task} обновлено!")
    await dialog_manager.switch_to(OperatorTasksSG.client_task_card)


async def on_approve_task(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
):
    """Handler for approving client task."""
    task_id = dialog_manager.dialog_data.get("task_id")
    
    if not task_id:
        await callback.answer("Ошибка: задание не найдено")
        return
    
    # Update task status to approved
    database.execute(
        update(tasks_table)
        .where(tasks_table.c.id == task_id)
        .where(tasks_table.c.status == 0)
        .values(status=1)
    )
    
    await callback.answer("Задания приняты!")
    await callback.message.answer("Задания студента одобрены")
    await dialog_manager.switch_to(OperatorTasksSG.client_selection)


async def on_reject_task(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
):
    """Handler for rejecting client task."""
    task_id = dialog_manager.dialog_data.get("task_id")
    client_id = dialog_manager.dialog_data.get("selected_client_id")
    
    if not task_id:
        await callback.answer("Ошибка: задание не найдено")
        return
    
    # Update task status to rejected
    database.execute(
        update(tasks_table)
        .where(tasks_table.c.id == task_id)
        .where(tasks_table.c.status == 0)
        .values(status=2)
    )
    
    # Notify client
    if client_id:
        bot = dialog_manager.middleware_data.get("bot")
        if bot:
            await bot.send_message(
                client_id,
                "<b>Ваши задания были отклонены!</b> Пожалуйста, перепишите их и снова отправьте!",
                parse_mode=ParseMode.HTML,
            )
    
    await callback.answer("Задания отклонены!")
    await callback.message.answer("Задания студента отклонены")
    await dialog_manager.switch_to(OperatorTasksSG.client_selection)


async def on_approve_end_session(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
):
    """Handler for approving end of session."""
    task_id = dialog_manager.dialog_data.get("task_id")
    
    if not task_id:
        await callback.answer("Ошибка: задание не найдено")
        return
    
    # Update task status to completed
    database.execute(
        update(tasks_table)
        .where(tasks_table.c.id == task_id)
        .values(status=3)
    )
    
    await callback.answer("Сессия завершена!")
    await callback.message.answer("Сессия студента завершена")
    await dialog_manager.switch_to(OperatorTasksSG.client_selection)


async def on_reject_end_session(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
):
    """Handler for rejecting end of session."""
    await callback.answer("Завершение сессии отклонено")
    await callback.message.answer("Завершение сессии отклонено - студент может продолжать работу")
    await dialog_manager.switch_to(OperatorTasksSG.client_selection)
