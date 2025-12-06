from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back, Cancel

from bot.modules.groups.handlers import (
    on_add_specific_user, 
    on_add_user_group, 
    on_remove_specific_user,
    on_remove_user_group,
    on_delete_group,
    on_confirm_group_creation, 
    on_group_title_input
)
from bot.modules.states import ClientGroupsStates, OperatorGroupsStates, OperatorGroupCreateStates
from bot.modules.users.handlers import get_operator_students_data


def create_group_dialogs():
    from bot.modules.groups.handlers import (
        get_all_groups_data,

        on_back_to_profile,
        # on_group_tasks,
        on_group_create,
        on_group_select,
        on_group_tasks_clicked,
        getter_group_clients,
        getter_group_clients_for_removal,
        getter_client_group_info,
        on_group_tasks_clicked_client,
    )

    # Диалог для управления группами (OperatorGroupsStates)
    operator_group_window = Window(
        Format(
            "👥 <b>Список групп</b>\n\n"
            "📊 Всего групп: {total_groups}\n"
            "📄 Страницы {current_page} из {total_pages}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("👥 {item[name]}"),
                id="group_select",
                item_id_getter=lambda x: str(x["name"]),
                items="groups_page",
                on_click=on_group_select,
            ),
            id="groups_scroll",
            width=1,
            height=5,
        ),
        Button(
            Const("➕ Создать группу"),
            id="create_group",
            on_click=on_group_create,
        ),
        Button(
            Const("🔙 В профиль"),
            id="back_to_profile",
            on_click=on_back_to_profile,
        ),
        getter=get_all_groups_data,
        state=OperatorGroupsStates.GROUP_LIST,
    )

    operator_group_actions = Window(
        Format(
            "🏠 <b>Управление группой</b>\n\n"
            "👥 <b>Участники:</b>\n{students_text}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),

        Button(
            Const("📝 Задачи группы"),
            id="group_tasks",
            on_click=on_group_tasks_clicked,
        ),
        Row(
            Button(
                Const("➕ Добавить"),
                id="add_member",
                on_click=on_add_user_group,
            ),
            Button(
                Const("➖ Удалить"),
                id="remove_member",
                on_click=on_remove_user_group,
            )
        ),
        Button(Const("🗑️ Удалить группу"),
               id="delete_group",
               on_click=on_delete_group,
               ),
        Back(Const("🔙 Назад")),
        getter=getter_group_clients,
        state=OperatorGroupsStates.GROUP_ACTIONS,
    )

    operator_add_user_window = Window(
        Format(
            "➕ <b>Добавить участника</b>\n\n"
            "🎯 Выберите студента для добавления в группу:\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("🎓 {item[first_name]} {item[last_name]}"),
                id="student_select",
                item_id_getter=lambda x: str(x["telegram_id"]),
                items="students_page",
                on_click=on_add_specific_user,
            ),
            id="students_scroll",
            width=1,
            height=5,  
        ),
        Back(Const("Назад")),
        getter=get_operator_students_data,
        state=OperatorGroupsStates.GROUP_ADD_USER,
    )

    operator_remove_user_window = Window(
        Format(
            "➖ <b>Удалить участника</b>\n\n"
            "⚠️ Выберите участника для удаления из группы:\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("❌ {item[first_name]} {item[last_name]}"),
                id="client_select",
                item_id_getter=lambda x: str(x["telegram_id"]),
                items="clients_page",
                on_click=on_remove_specific_user,
            ),
            id="clients_scroll",
            width=1,
            height=5,
        ),
        # Back(Const("Назад")),
        Button(
            Const("🔙 Назад"),
            id="back_to_actions",
            on_click=lambda c, b, m: m.switch_to(OperatorGroupsStates.GROUP_ACTIONS),
        ),
        getter=getter_group_clients_for_removal,
        state=OperatorGroupsStates.GROUP_REMOVE_USER,
    )

    # Первый диалог - только для OperatorGroupsStates
    operator_groups_dialog = Dialog(
        operator_group_window,
        operator_group_actions,
        operator_add_user_window,
        operator_remove_user_window,
    )

    # Второй диалог - только для OperatorGroupCreateStates
    create_group_name_window = Window(
        Const(
            "➕ <b>Создание группы</b>\n\n"
            "🏷️ Шаг 1 из 3: Введите название группы\n"
            "💡 <i>Пример: 'Группа Математика 10А'</i>"
        ),
        TextInput(
            id="group_name_input",
            type_factory=str,
            on_success=on_group_title_input,
        ),
        Back(Const("❌ Отменить")),
        state=OperatorGroupCreateStates.CREATE_GROUP_NAME
    )

    create_group_description_window = Window(
        Const(
            "➕ <b>Создание группы</b>\n\n"
            "📝 Шаг 2 из 3: Введите описание группы\n"
            "💡 <i>Пример: 'Группа для студентов 10 класса по математике'</i>"
        ),
        TextInput(
            id="group_description_input",
            type_factory=str,
            on_success=lambda m, w, d, data: d.dialog_data.update(
                {"group_description": data}) or d.switch_to(OperatorGroupCreateStates.CREATE_GROUP_CONFIRM),
        ),
        Back(Const("Назад")),
        state=OperatorGroupCreateStates.CREATE_GROUP_DESCRIPTION
    )

    create_group_confirm_window = Window(
        Format(
            "➕ <b>Создание группы</b>\n\n"
            "✅ Шаг 3 из 3: Подтверждение\n\n"
            "🏷️ <b>Название:</b> {dialog_data[group_title]}\n"
            "📝 <b>Описание:</b> {dialog_data[group_description]}\n\n"
            "✅ Все верно?"
        ),
        Row(
            Button(
                Const("✅ Подтвердить"),
                id="confirm_group_creation",
                on_click=on_confirm_group_creation,
            ),
            Button(
                Const("❌ Отмена"),
                id="cancel_group_creation",
                on_click=lambda c, b, d: d.dialog_data.clear(
                ) or d.switch_to(OperatorGroupsStates.GROUP_LIST),
            ),
        ),
        state=OperatorGroupCreateStates.CREATE_GROUP_CONFIRM
    )
    create_group_dialog = Dialog(
        create_group_name_window,
        create_group_description_window,
        create_group_confirm_window,
    )

    client_groups_dialog = Dialog(
        Window(
            Format(
                "🏠 <b>Информация о группе</b>\n\n"
                "🏷️ <b>Название:</b> {name}\n\n"
                "📝 <b>Описание:</b> {description}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
            ),
            Button(
                Const("📝 Задачи группы"),
                id="client_group_tasks",
                on_click=on_group_tasks_clicked_client,
            ),
            Cancel(Const("🔙 Назад")),
            getter=getter_client_group_info,
            state=ClientGroupsStates.GROUP_INFO,
        )
    )

    # Возвращаем оба диалога
    return operator_groups_dialog, create_group_dialog, client_groups_dialog
