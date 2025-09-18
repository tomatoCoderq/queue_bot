"""Windows for auth module using aiogram_dialog."""

from typing import Any

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import (
    Dialog, DialogManager, Window, ShowMode,
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button, Column, Row, Select, Start, Back
)
from aiogram_dialog.widgets.text import Const, Format

from src.modules.auth.states import AuthSG
from src.modules.tasks.states import TasksSG
from src.modules.operator.states import OperatorTasksSG
from src.modules.shared.messages import KeyboardTitles, RegistrationMessages
from src.modules.auth.handlers.registration_handlers import (
    process_student_registration,
    process_teacher_registration,
    on_student_role_selected,
    on_teacher_role_selected,
    on_cancel_teacher,
    on_menu_action,
)

# ==================== CHOOSE ROLE WINDOW ====================

async def choose_role_getter(**kwargs):
    """Getter for choose role window."""
    return {
        "welcome_text": RegistrationMessages.welcome_message,
        "student_title": KeyboardTitles.start_registration_client,
        "teacher_title": KeyboardTitles.start_registration_operator,
    }


choose_role_window = Window(
    Format("{welcome_text}"),
    Row(
        Button(
            Format("{student_title}"),
            id="student_role",
            on_click=on_student_role_selected,
        ),
        Button(
            Format("{teacher_title}"),
            id="teacher_role", 
            on_click=on_teacher_role_selected,
        ),
    ),
    getter=choose_role_getter,
    state=AuthSG.choose_role,
)


# ==================== STUDENT NAME INPUT WINDOW ====================

async def student_name_getter(**kwargs):
    """Getter for student name input window."""
    return {
        "name_prompt": RegistrationMessages.student_provide_name,
    }


student_name_input_window = Window(
    Format("{name_prompt}"),
    TextInput(
        id="name_input",
        type_factory=str,
        on_success=process_student_registration,
    ),
    getter=student_name_getter,
    state=AuthSG.student_name_input,
)


# ==================== TEACHER CONFIRM WINDOW ====================

async def teacher_confirm_getter(**kwargs):
    """Getter for teacher confirmation window."""
    return {
        "confirm_text": "🔐 Подтвердите выбор роли Оператора",
        "confirm_button": "✅ Подтвердить",
        "cancel_button": "❌ Отмена",
    }


teacher_confirm_window = Window(
    Format("{confirm_text}"),
    Row(
        Button(
            Format("{confirm_button}"),
            id="confirm_teacher",
            on_click=process_teacher_registration,
        ),
        Button(
            Format("{cancel_button}"),
            id="cancel_teacher",
            on_click=on_cancel_teacher,
        ),
    ),
    getter=teacher_confirm_getter,
    state=AuthSG.teacher_confirm,
)


# ==================== MAIN MENU WINDOWS ====================

async def student_menu_getter(**kwargs):
    """Getter for student main menu."""
    return {
        "welcome_text": "👤 Добро пожаловать, Клиент!",
        "upload_detail": KeyboardTitles.upload_detail,
        "task_queue": KeyboardTitles.task_queue,
        "tasks": KeyboardTitles.tasks,
        "equipment": "📦 Комплектующие",
    }


student_menu_window = Window(
    Format("{welcome_text}"),
    Column(
        Button(
            Format("{upload_detail}"),
            id="upload_detail",
            on_click=on_menu_action,
        ),
        Button(
            Format("{task_queue}"),
            id="task_queue",
            on_click=on_menu_action,
        ),
        Start(
            Format("{tasks}"),
            id="tasks",
            state=TasksSG.view_tasks,
        ),
        Button(
            Format("{equipment}"),
            id="equipment",
            on_click=on_menu_action,
        ),
    ),
    getter=student_menu_getter,
    state=AuthSG.main_menu_student,
)


async def teacher_menu_getter(**kwargs):
    """Getter for teacher main menu."""
    return {
        "welcome_text": "👥 Добро пожаловать, Оператор!",
        "open_queue": KeyboardTitles.open_queue,
        "client_tasks": KeyboardTitles.client_tasks,
        "history": KeyboardTitles.history,
        "get_xlsx": KeyboardTitles.get_xlsx,
    }


teacher_menu_window = Window(
    Format("{welcome_text}"),
    Column(
        Button(
            Format("{open_queue}"),
            id="open_queue",
            on_click=on_menu_action,
        ),
        Start(
            Format("{client_tasks}"),
            id="client_tasks",
            state=OperatorTasksSG.tasks_main_menu,
        ),
        Button(
            Format("{history}"),
            id="history",
            on_click=on_menu_action,
        ),
        Button(
            Format("{get_xlsx}"),
            id="get_xlsx",
            on_click=on_menu_action,
        ),
    ),
    getter=teacher_menu_getter,
    state=AuthSG.main_menu_teacher,
)
