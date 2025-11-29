from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Group

from bot.modules.states import OperatorStudentsStates

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Cancel, Back
from bot.modules.states import (
    OperatorStudentsStates,
)

def create_user_dialogs():
    from bot.modules.users.handlers import (
        on_client_tasks,
        on_client_penalties,
        on_client_details,
        getter_client_card,
        on_student_select,
        get_operator_students_data,
    )
    
    operator_students_window = Window(
        Format(
            "👥 <b>Список студентов</b>\n\n"
            "📊 Всего студентов: {total_students}\n"
            "📄 Страница {current_page} из {total_pages}\n"
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
            height=5,  # Max 5 students per page
        ),
        # Button(
        #     Const("🔙 В профиль"),
        #     id="back_to_profile",
        #     on_click=on_back_to_profile,
        # ),
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
            Back(Const("🔙 Назад")),
        ),
        getter=getter_client_card,
        state=OperatorStudentsStates.STUDENTS_INFO,
    )
    
    client_dialog = Dialog(
        operator_students_window,
        client_card_window,
   
    )
    
    return client_dialog

