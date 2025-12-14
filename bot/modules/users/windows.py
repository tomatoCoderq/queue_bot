from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Group

from bot.modules.states import OperatorStudentsStates

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Cancel, Back, Row
from aiogram_dialog.widgets.input import TextInput
from bot.modules.states import (
    OperatorStudentsStates,
    OperatorUpdateUserStates,
)

def create_user_dialogs():
    from bot.modules.users.handlers import (
        on_client_tasks,
        on_client_penalties,
        on_client_details,
        getter_client_card,
        on_student_select,
        get_operator_students_data,
        on_delete_student_click,
        getter_delete_confirmation,
        on_confirm_delete_student,
        on_update_student_click,
        on_role_select,
        on_update_first_name,
        on_update_last_name,
        getter_update_confirmation,
        on_confirm_update_user,
    )
    
    operator_students_window = Window(
        Format(
            "👥 <b>Список студентов</b>\n\n"
            "📊 Всего студентов: {total_students}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("🎓 {item[first_name]} {item[last_name]}"),
                id="student_select",
                item_id_getter=lambda x: str(x["telegram_id"]),
                items="students_page",
                on_click=on_student_select,
            ),
            id="students_scroll",
            width=1,
            height=5,
        ),
        Cancel(Const("🔙 В профиль")),
        getter=get_operator_students_data,
        state=OperatorStudentsStates.STUDENTS_LIST,
    )
    
    client_card_window = Window(
        Format(
            "🎓 <b>Профиль студента</b>\n\n"
            "👤 <b>Имя:</b> {name}\n"
            "🆔 <b>Telegram ID:</b> {telegram_id}\n\n"
            "📊 <b>Статистика:</b>\n"
            "📝 Количество задач: {tasks}\n"
            "⚠️ Количество штрафов: {penalties}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        Group(
            Button(
                Const("📝 Задачи"),
                id="client_tasks_button",
                on_click=on_client_tasks,
            ),
            Button(
                Const("⚠️ Штрафы"),
                id="client_penalties_button",
                on_click=on_client_penalties,
            ),
            Button(
                Const("🖨 Принты"),
                id="client_details_button",
                on_click=on_client_details,
            ),
            Button(
                Const("✏️ Обновить данные"),
                id="update_student_button",
                on_click=on_update_student_click,
            ),
            Button(
                Const("🗑️ Удалить студента"),
                id="delete_student_button",
                on_click=on_delete_student_click,
            ),
            Back(Const("🔙 Назад")),
        ),
        getter=getter_client_card,
        state=OperatorStudentsStates.STUDENTS_INFO,
    )

    client_delete_confirm_window = Window(
        Format(
            "⚠️ <b>Удаление студента</b>\n\n"
            "Вы уверены, что хотите удалить студента {student_name}?\n"
            "Действие нельзя отменить."
        ),
        Group(
            Button(
                Const("✅ Подтвердить"),
                id="confirm_delete_student",
                on_click=on_confirm_delete_student,
            ),
            # Button(
            #     Const("🔙 Отмена"),
            #     id="cancel_delete_student",
            #     on_click=lambda c, b, m: m.start(OperatorStudentsStates.STUDENTS_LIST)
            # )
            Back(Const("🔙 Отмена")),
            
        ),
        getter=getter_delete_confirmation,
        state=OperatorStudentsStates.STUDENTS_DELETE_CONFIRM,
    )

    # Windows for updating user data
    update_user_role_window = Window(
        Const(
            "✏️ <b>Обновление данных студента</b>\n\n"
            "🎯 Шаг 1 из 3: Выберите новую роль\n"
        ),
        Group(
            Select(
                Format("{item}"),
                id="role_select",
                item_id_getter=lambda x: x,
                items=["Студент", "Оператор"],
                on_click=on_role_select,
            ),
            Button(Const("⏭️ Пропустить"), id="skip_role", on_click=lambda c, b, m: m.switch_to(OperatorUpdateUserStates.UPDATE_USER_FIRST_NAME)),
        ),
        Cancel(Const("🔙 Отмена")),
        state=OperatorUpdateUserStates.UPDATE_USER_ROLE,
    )

    update_user_first_name_window = Window(
        Const(
            "✏️ <b>Обновление данных студента</b>\n\n"
            "🎯 Шаг 2 из 3: Введите новое имя\n"
        ),
        TextInput(
            id="first_name_input",
            type_factory=str,
            on_success=on_update_first_name,
        ),
        Button(Const("⏭️ Пропустить"), id="skip_first_name", on_click=lambda c, b, m: m.switch_to(OperatorUpdateUserStates.UPDATE_USER_LAST_NAME)),
        Back(Const("🔙 Отмена")),
        state=OperatorUpdateUserStates.UPDATE_USER_FIRST_NAME,
    )

    update_user_last_name_window = Window(
        Const(
            "✏️ <b>Обновление данных студента</b>\n\n"
            "🎯 Шаг 3 из 3: Введите новую фамилию\n"
        ),
        TextInput(
            id="last_name_input",
            type_factory=str,
            on_success=on_update_last_name,
        ),
        Button(Const("⏭️ Пропустить"), id="skip_last_name", on_click=lambda c, b, m: m.switch_to(OperatorUpdateUserStates.UPDATE_USER_CONFIRM)),
        Back(Const("🔙 Отмена")),
        state=OperatorUpdateUserStates.UPDATE_USER_LAST_NAME,
    )

    update_user_confirm_window = Window(
        Format(
            "✏️ <b>Обновление данных студента</b>\n\n"
            "✅ Подтверждение\n\n"
            "👤 <b>Студент:</b> {student_name}\n"
            "🎯 <b>Новая роль:</b> {new_role}\n"
            "📝 <b>Новое имя:</b> {new_first_name}\n"
            "📝 <b>Новая фамилия:</b> {new_last_name}\n\n"
            "✅ Все верно?"
        ),
        Group(
            Button(
                Const("✅ Подтвердить"),
                id="confirm_update_user",
                on_click=on_confirm_update_user,
            ),
            Back(Const("🔙 Отмена")),
        ),
        getter=getter_update_confirmation,
        state=OperatorUpdateUserStates.UPDATE_USER_CONFIRM,
    )

    # Dialog for updating user
    update_user_dialog = Dialog(
        update_user_role_window,
        update_user_first_name_window,
        update_user_last_name_window,
        update_user_confirm_window,
    )
    
    client_dialog = Dialog(
        operator_students_window,
        client_card_window,
        client_delete_confirm_window,
    )
    
    return client_dialog, update_user_dialog

