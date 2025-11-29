from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Row, Group
from aiogram_dialog.widgets.input import TextInput

from bot.modules.states import RegistrationStates, ProfileStates

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
        get_profile_data,
        on_menu_tasks,
        on_menu_settings,
        on_menu_review_tasks,
        on_groups_tasks,
    )

    # Window 2: Role Choice
    role_choice_window = Window(
        Const("<b>Выберите вашу роль:</b>\n\n"
              "👤 <b>Student</b> - Студент (может просматривать свои задачи)\n"
              "👨‍👩‍👧 <b>Parent</b> - Родитель (<i>в разработке</i>)\n"
              "⚙️ <b>Operator</b> - Оператор (может управлять задачами студентов)"),
        Row(
            Button(
                Const("👤 Студент"),
                id="role_student",
                on_click=on_role_select,
            ),
            Button(
                Const("👨‍👩‍ Родитель"),
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
        Const("<b>Введите ваше имя:</b>"),
        TextInput(
            id="first_name_input",
            type_factory=str,
            on_success=on_first_name_input,
        ),
        state=RegistrationStates.FIRST_NAME,
    )

    # Window 4: Last Name Input
    last_name_window = Window(
        Const("<b>Введите вашу фамилию:</b>"),
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
            "✅ <b>Проверьте ваши данные:</b>\n\n"
            "<b>Роль:</b> {dialog_data[role]}\n"
            "<b>Имя:</b> {dialog_data[first_name]}\n"
            "<b>Фамилия:</b> {dialog_data[last_name]}\n"
            "<b>Username:</b> {dialog_data[username]}\n\n"
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
        Const("🎉 <b>Поздравляем с регистрацией!</b>\n\n"
              "✅ Вы успешно зарегистрированы в системе.\n"
              "✨ Нажмите <code>/start</code> чтобы войти в профиль."),
        # getter=on_success_complete,
        state=RegistrationStates.SUCCESS,
    )


    profile_window = Window(
        Format(
            "👤 <b>Ваш профиль</b>\n\n"
            "<b>Имя:</b> {first_name} {last_name}\n"
            "<b>Роль:</b> {role_display}\n"
            "<b>Username:</b> {username}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        Group(
            Button(
                Format("{tasks_button_text}"),
                id="menu_tasks",
                on_click=on_menu_tasks,
            ),
            Button(
                Format("👥 Группы"),
                id="menu_groups",
                on_click=on_groups_tasks,
                # when="is_operator",
            ),
            Button(
                Const("📝 Задачи на проверке"),
                id="menu_review_tasks",
                on_click=on_menu_review_tasks,
                when="is_operator",
            ),
            Button(
                Const("🖨 Принты"),
                id="menu_prints",
                on_click=lambda c, b, m: c.answer("🔧 Функция принтов находится в процессе разработки.", show_alert=True),
                # on_click=on_menu_prints, 
            ),
            Button(
                Const("⚙️ Настройки"),
                id="menu_settings",
                on_click=on_menu_settings,
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
        launch_mode=LaunchMode.ROOT
    )
    
    return registration_dialog, profile_dialog

