"""Windows for tasks module using aiogram_dialog."""

import datetime
import os
from typing import Any, Dict

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Column, Group, Row, Back
from aiogram_dialog.widgets.text import Const, Format
from loguru import logger
from sqlalchemy import func, select, insert, update, text

from src.modules.tasks.states import TasksSG
from src.modules.shared.messages import StudentMessages, KeyboardTitles
from src.storages.sql.dependencies import database
from src.storages.sql.models import TaskModel, tasks_table


# ==================== GETTERS ====================

async def tasks_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for tasks view window."""
    user_id = dialog_manager.event.from_user.id
    
    # Get current tasks
    tasks = database.fetch_all(
        select(tasks_table)
        .where(tasks_table.c.idt == user_id)
        .where(tasks_table.c.status.in_([1, 5]))
        .where(func.date(tasks_table.c.start_time) == func.current_date())
        .order_by(tasks_table.c.id),
        model=TaskModel,
    )
    
    if not tasks:
        return {
            "tasks_text": StudentMessages.NO_TASKS,
            "has_tasks": False,
        }
    
    current = tasks[-1]
    tasks_text = f"<b>Задачи на сегодня:</b>\n(1) {current.task_first}\n(2) {current.task_second}"
    
    return {
        "tasks_text": tasks_text,
        "has_tasks": True,
    }


async def submit_first_task_getter(**kwargs) -> Dict[str, Any]:
    """Getter for first task input window."""
    return {
        "prompt": StudentMessages.WRITE_FIRST_TASK_TO_SUBMIT,
    }


async def submit_second_task_getter(**kwargs) -> Dict[str, Any]:
    """Getter for second task input window."""
    return {
        "prompt": StudentMessages.WRITE_SECOND_TASK_TO_SUBMIT,
    }


async def close_tasks_getter(**kwargs) -> Dict[str, Any]:
    """Getter for close tasks confirmation window."""
    return {
        "confirmation_text": "Вы уверены, что хотите завершить текущие задания?",
        "invite_text": StudentMessages.INVITE_OPERATOR_FOR_APPROVE,
    }


async def end_task_getter(**kwargs) -> Dict[str, Any]:
    """Getter for ending current task window."""
    return {
        "prompt": "OK, пиши новое задание номер два",
    }


async def continue_task_getter(**kwargs) -> Dict[str, Any]:
    """Getter for continue task options window."""
    return {
        "text": "Выберите количество дополнительного времени:",
    }


# ==================== WINDOWS ====================

from src.modules.tasks.handlers.dialog_handlers import (
    on_submit_tasks_clicked,
    on_close_tasks_clicked,
    process_first_task,
    process_second_task,
    confirm_close_tasks,
    on_end_current_task,
    process_new_second_task,
    on_continue_task,
    add_10_minutes,
    add_15_minutes,
    add_30_minutes,
)

# Main tasks view window
view_tasks_window = Window(
    Format("{tasks_text}"),
    Column(
        Button(
            Const("📝 Подать задания"),
            id="submit_tasks",
            on_click=on_submit_tasks_clicked,
            when="has_tasks",
        ),
        Button(
            Const("✅ Завершить задания"),
            id="close_tasks",
            on_click=on_close_tasks_clicked,
            when="has_tasks",
        ),
        Button(
            Const("📝 Подать задания"),
            id="submit_tasks_no_tasks",
            on_click=on_submit_tasks_clicked,
            when=~F["has_tasks"],
        ),
    ),
    Back(Const("🔙 Назад")),
    getter=tasks_getter,
    state=TasksSG.view_tasks,
)

# First task input window
submit_first_task_window = Window(
    Format("{prompt}"),
    TextInput(
        id="first_task_input",
        type_factory=str,
        on_success=process_first_task,
    ),
    Back(Const("🔙 Назад")),
    getter=submit_first_task_getter,
    state=TasksSG.submit_task_first,
)

# Second task input window
submit_second_task_window = Window(
    Format("{prompt}"),
    TextInput(
        id="second_task_input",
        type_factory=str,
        on_success=process_second_task,
    ),
    Back(Const("🔙 Назад")),
    getter=submit_second_task_getter,
    state=TasksSG.submit_task_second,
)

# Close tasks confirmation window
close_tasks_window = Window(
    Format("{confirmation_text}"),
    Row(
        Button(
            Const("✅ Да, завершить"),
            id="confirm_close",
            on_click=confirm_close_tasks,
        ),
        Button(
            Const("❌ Отмена"),
            id="cancel_close",
            on_click=lambda c, w, d: d.switch_to(TasksSG.view_tasks),
        ),
    ),
    Back(Const("🔙 Назад")),
    getter=close_tasks_getter,
    state=TasksSG.close_tasks_confirm,
)

# End current task window
end_task_window = Window(
    Format("{prompt}"),
    TextInput(
        id="new_second_task_input",
        type_factory=str,
        on_success=process_new_second_task,
    ),
    Back(Const("🔙 Назад")),
    getter=end_task_getter,
    state=TasksSG.add_new_second_task,
)

# Continue task options window
continue_task_window = Window(
    Format("{text}"),
    Column(
        Button(
            Const("⏱ +10 минут"),
            id="add_10",
            on_click=add_10_minutes,
        ),
        Button(
            Const("⏱ +15 минут"),
            id="add_15",
            on_click=add_15_minutes,
        ),
        Button(
            Const("⏱ +30 минут"),
            id="add_30",
            on_click=add_30_minutes,
        ),
    ),
    Back(Const("🔙 Назад")),
    getter=continue_task_getter,
    state=TasksSG.continue_task_options,
)
