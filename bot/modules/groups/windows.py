from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Row, Group
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back

from bot.modules.groups.handlers import on_confirm_group_creation, on_group_title_input
from bot.modules.states import OperatorGroupsStates, OperatorGroupCreateStates


def create_group_dialogs():
    from bot.modules.groups.handlers import (
        get_all_groups_data,
        
        on_back_to_profile,
        # on_group_tasks,
        on_group_create,
        on_group_select,
        on_group_tasks_clicked
    )
    
    from bot.modules.tasks.handlers import (
        on_page_next,
        on_page_prev,
    )

    # Диалог для управления группами (OperatorGroupsStates)
    operator_group_window = Window(
        Format(
            "Список групп\n\n"
            "Всего групп: {total_groups}\n"
            "Страницы {current_page} из {total_pages}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("{item[name]}"),
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
            Const("+"),
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

    # operator_group_data = Window(
    #     Format(
    #         "👥 Список групп\n\n"
    #         "Всего групп: {total_groups}\n"
    #         "Страница {current_page} из {total_pages}\n"
    #         "━━━━━━━━━━━━━━━━━━━━━━\n"
    #     ),
    #     ScrollingGroup(
    #         Select(
    #             Format("{item[name]}"),
    #             id="group_select",
    #             item_id_getter=lambda x: str(x["name"]),
    #             items="groups_page",
    #             on_click=on_group_tasks,
    #         ),
    #         id="groups_scroll",
    #         width=1,
    #         height=5,  # Max 5 groups per page
    #     ),
    #     Row(
    #         Button(
    #             Const("◀️ Назад"),
    #             id="page_prev",
    #             on_click=on_page_prev,
    #             when="has_prev",
    #         ),
    #         Button(
    #             Const("Вперёд ▶️"),
    #             id="page_next",
    #             on_click=on_page_next,
    #             when="has_next",
    #         ),
    #     ),
    #     Button(
    #         Const("🔙 В профиль"),
    #         id="back_to_profile",
    #         on_click=on_back_to_profile,
    #     ),
    #     getter=get_all_groups_data,
    #     state=OperatorGroupsStates.GROUP_LIST,
    # )


    # Первый диалог - только для OperatorGroupsStates
    operator_groups_dialog = Dialog(
        operator_group_window,
        # добавить другие окна из OperatorGroupsStates если есть
    )

    # Второй диалог - только для OperatorGroupCreateStates
    create_group_name_window = Window(
        Const("Создание группы\nВведите название группы:"),
        TextInput(
            id="group_name_input",
            type_factory=str,
            on_success=on_group_title_input,
        ),
        Back(Const("Отменить")),
        state=OperatorGroupCreateStates.CREATE_GROUP_NAME
    )

    create_group_description_window = Window(
        Const("Введите описание группы:"),
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
            "Пожалуйста, подтвердите создание группы:\n\n"
            "Название: {dialog_data[group_title]}\n"
            "Описание: {dialog_data[group_description]}\n\n"
            "Все верно?"
        ),
        Row(
            Button(
                Const("✅ Подтвердить"),
                id="confirm_group_creation",
                on_click=on_confirm_group_creation,
            ),
            Button(
                Const("❌ Отменить"),
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

    # Возвращаем оба диалога
    return operator_groups_dialog, create_group_dialog
