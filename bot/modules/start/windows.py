from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Row, Group
from aiogram_dialog.widgets.input import TextInput


class RegistrationStates(StatesGroup):
    ROLE_CHOICE = State()
    FIRST_NAME = State()
    LAST_NAME = State()
    CONFIRM = State()
    SUCCESS = State()


class ProfileStates(StatesGroup):
    PROFILE = State()


# States for Students
class StudentStates(StatesGroup):
    MY_TASKS = State()
    TASK_DETAIL = State()


# States for Operators
class OperatorStates(StatesGroup):
    STUDENTS_LIST = State()
    STUDENT_TASKS = State()
    TASK_DETAIL = State()


def create_dialogs():
    """
    Create dialogs with handlers imported from handlers module.
    This function should be called after handlers are defined.
    """
    # Import handlers here to avoid circular imports
    from bot.modules.start.handlers import (
        on_role_select,
        on_first_name_input,
        on_last_name_input,
        on_confirm_registration,
        on_cancel_registration,
        on_success_complete,
        get_profile_data,
        on_menu_tasks,
        on_menu_settings,
        on_menu_logout,
    )

    # Window 2: Role Choice
    role_choice_window = Window(
        Const("Выберите вашу роль:\n\n"
              "👤 Student - Студент (может просматривать свои задачи)\n"
              "�‍👩‍👧 Parent - Родитель (в разработке)\n"
              "⚙️ Operator - Оператор (может управлять задачами студентов)"),
        Row(
            Button(
                Const("👤 Студент"),
                id="role_student",
                on_click=on_role_select,
            ),
            Button(
                Const("👨‍👩‍� Родитель"),
                id="role_parent",
                on_click=on_role_select,
            ),
        ),
        Button(
            Const("⚙️ Оператор"),
            id="role_operator",
            on_click=on_role_select,
        ),
        state=RegistrationStates.ROLE_CHOICE,
    )

    first_name_window = Window(
        Const("Введите ваше имя:"),
        TextInput(
            id="first_name_input",
            type_factory=str,
            on_success=on_first_name_input,
        ),
        state=RegistrationStates.FIRST_NAME,
    )

    # Window 4: Last Name Input
    last_name_window = Window(
        Const("Введите вашу фамилию:"),
        TextInput(
            id="last_name_input",
            type_factory=str,
            on_success=on_last_name_input,
        ),
        state=RegistrationStates.LAST_NAME,
    )

    # Window 5: Confirm Registration
    confirm_window = Window(
        Format(
            "✅ Проверьте ваши данные:\n\n"
            "Роль: {dialog_data[role]}\n"
            "Имя: {dialog_data[first_name]}\n"
            "Фамилия: {dialog_data[last_name]}\n"
            "Username: {dialog_data[username]}\n\n"
            "Все верно?"
        ),
        Row(
            Button(
                Const("✅ Да, зарегистрировать"),
                id="confirm_yes",
                on_click=on_confirm_registration,
            ),
            Button(
                Const("❌ Отменить"),
                id="confirm_no",
                on_click=on_cancel_registration,
            ),
        ),
        state=RegistrationStates.CONFIRM,
    )

    # Window 6: Success Message
    success_window = Window(
        Const("Поздравляем с регистрацией!\n\n"
              "Вы успешно зарегистрированы в системе.\n"
              "Нажмите /start чтобы войти в профиль."),
        getter=on_success_complete,
        state=RegistrationStates.SUCCESS,
    )


    profile_window = Window(
        Format(
            "👤 Ваш профиль\n\n"
            "Имя: {first_name} {last_name}\n"
            "Роль: {role_display}\n"
            "Username: {username}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        Group(
            Button(
                Format("{tasks_button_text}"),
                id="menu_tasks",
                on_click=on_menu_tasks,
            ),
            Button(
                Const("⚙️ Настройки"),
                id="menu_settings",
                on_click=on_menu_settings,
            ),
            Button(
                Const("🚪 Выход"),
                id="menu_logout",
                on_click=on_menu_logout,
            ),
        ),
        getter=get_profile_data,
        state=ProfileStates.PROFILE,
    )


    registration_dialog = Dialog(
        role_choice_window,
        first_name_window,
        last_name_window,
        confirm_window,
        success_window,
    )

    profile_dialog = Dialog(
        profile_window,
    )
    
    return registration_dialog, profile_dialog

