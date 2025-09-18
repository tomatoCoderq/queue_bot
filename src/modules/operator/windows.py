"""Windows for operator tasks module using aiogram_dialog."""

import datetime
from typing import Any, Dict

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Column, Row, Select, Back
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy import select, func

from src.modules.operator.states import OperatorTasksSG
from src.modules.shared.messages import KeyboardTitles
from src.storages.sql.dependencies import database
from src.storages.sql.models import StudentModel, students_table, TaskModel, tasks_table


# ==================== GETTERS ====================

async def tasks_main_menu_getter(**kwargs) -> Dict[str, Any]:
    """Getter for operator tasks main menu."""
    return {
        "welcome_text": "👥 Управление заданиями студентов",
        "client_tasks": KeyboardTitles.client_tasks,
        "history": KeyboardTitles.history,
        "get_xlsx": KeyboardTitles.get_xlsx,
    }


async def client_selection_getter(**kwargs) -> Dict[str, Any]:
    """Getter for client selection window."""
    # Get all students
    records = database.fetch_all(
        select(students_table.c.idt, students_table.c.name, students_table.c.surname)
        .order_by(students_table.c.surname),
        model=StudentModel,
    )
    
    clients = []
    for record in records:
        clients.append({
            "id": record.idt,
            "name": f"{record.surname} {record.name}",
            "full_text": f"{record.surname} {record.name} | {record.idt}",
        })
    
    return {
        "instruction_text": "Выберите студента для просмотра заданий:",
        "clients": clients,
    }


async def client_task_card_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for client task card window."""
    client_id = dialog_manager.dialog_data.get("selected_client_id")
    
    if not client_id:
        return {
            "task_info": "Студент не выбран",
            "has_tasks": False,
        }
    
    # Get current tasks for this client
    tasks = database.fetch_all(
        select(tasks_table)
        .where(tasks_table.c.idt == client_id)
        .where(tasks_table.c.status.in_([1, 5]))
        .where(func.date(tasks_table.c.start_time) == func.current_date())
        .order_by(tasks_table.c.id),
        model=TaskModel,
    )
    
    if not tasks:
        return {
            "task_info": "У студента нет активных заданий на сегодня",
            "has_tasks": False,
            "client_id": client_id,
        }
    
    latest_task = tasks[-1]
    start_time = latest_task.start_time + datetime.timedelta(hours=3)  # Moscow time
    
    task_info = (
        f"<b>Задания студента:</b>\n"
        f"(1) {latest_task.task_first}\n"
        f"(2) {latest_task.task_second}\n\n"
        f"<b>Начало:</b> {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"<b>Переносы:</b> {latest_task.shift}"
    )
    
    return {
        "task_info": task_info,
        "has_tasks": True,
        "client_id": client_id,
        "task_id": latest_task.id,
    }


async def change_task_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for task change window."""
    task_number = dialog_manager.dialog_data.get("changing_task", "1")
    return {
        "prompt": f"Введите новое задание номер {task_number}:",
    }


# ==================== WINDOWS ====================

from src.modules.operator.handlers.tasks_dialog_handlers import (
    on_client_tasks_clicked,
    on_history_clicked,
    on_get_xlsx_clicked,
    on_client_selected,
    on_change_task_one,
    on_change_task_two,
    process_task_change,
    on_approve_task,
    on_reject_task,
    on_approve_end_session,
    on_reject_end_session,
)

# Main tasks menu window
tasks_main_menu_window = Window(
    Format("{welcome_text}"),
    Column(
        Button(
            Format("{client_tasks}"),
            id="client_tasks",
            on_click=on_client_tasks_clicked,
        ),
        Button(
            Format("{history}"),
            id="history",
            on_click=on_history_clicked,
        ),
        Button(
            Format("{get_xlsx}"),
            id="get_xlsx",
            on_click=on_get_xlsx_clicked,
        ),
    ),
    Back(Const("🔙 Назад")),
    getter=tasks_main_menu_getter,
    state=OperatorTasksSG.tasks_main_menu,
)

# Client selection window
client_selection_window = Window(
    Format("{instruction_text}"),
    Select(
        text=Format("{item[full_text]}"),
        id="clients_select",
        items="clients",
        item_id_getter=lambda x: str(x["id"]),
        on_click=on_client_selected,
    ),
    Back(Const("🔙 Назад")),
    getter=client_selection_getter,
    state=OperatorTasksSG.client_selection,
)

# Client task card window
client_task_card_window = Window(
    Format("{task_info}"),
    Column(
        Row(
            Button(
                Const("✏️ Изменить задание 1"),
                id="change_task_1",
                on_click=on_change_task_one,
                when="has_tasks",
            ),
            Button(
                Const("✏️ Изменить задание 2"),
                id="change_task_2",
                on_click=on_change_task_two,
                when="has_tasks",
            ),
        ),
        Row(
            Button(
                Const("✅ Одобрить"),
                id="approve_task",
                on_click=on_approve_task,
                when="has_tasks",
            ),
            Button(
                Const("❌ Отклонить"),
                id="reject_task",
                on_click=on_reject_task,
                when="has_tasks",
            ),
        ),
        Row(
            Button(
                Const("🏁 Завершить сессию"),
                id="approve_end",
                on_click=on_approve_end_session,
                when="has_tasks",
            ),
            Button(
                Const("⏰ Отказать в завершении"),
                id="reject_end",
                on_click=on_reject_end_session,
                when="has_tasks",
            ),
        ),
    ),
    Back(Const("🔙 К списку студентов")),
    getter=client_task_card_getter,
    state=OperatorTasksSG.client_task_card,
)

# Change task one window
change_task_one_window = Window(
    Format("{prompt}"),
    TextInput(
        id="task_change_input",
        type_factory=str,
        on_success=process_task_change,
    ),
    Back(Const("🔙 Назад")),
    getter=change_task_getter,
    state=OperatorTasksSG.change_task_one,
)

# Change task two window
change_task_two_window = Window(
    Format("{prompt}"),
    TextInput(
        id="task_change_input",
        type_factory=str,
        on_success=process_task_change,
    ),
    Back(Const("🔙 Назад")),
    getter=change_task_getter,
    state=OperatorTasksSG.change_task_two,
)
