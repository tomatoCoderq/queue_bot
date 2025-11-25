from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput
from typing import Dict, Any


from bot.modules.groups import service

from bot.modules.states import OperatorTaskStates as TaskStates

router = Router()


async def get_all_groups_data(
        dialog_manager: DialogManager,
        **kwargs) -> Dict[str, Any]:
    current_page = dialog_manager.dialog_data.get("groups_page", 0)
    page_size = 5

    groups = await service.get_all_groups()
    total_groups = len(groups)
    total_pages = (total_groups + page_size -
                   1) // page_size if total_groups > 0 else 1

    start_index = current_page * page_size
    end_index = start_index + page_size
    paged_groups = groups[start_index:end_index]

    return {
        "groups_page": paged_groups,
        "total_groups": total_groups,
        "current_page": current_page + 1,
        "total_pages": total_pages,
        "has_prev": current_page > 0,
        "has_next": end_index < total_groups,
    }


# async def get_groups(dialog_manager: DialogManager):
#     group_id = dialog_manager.dialog_data.get("selected_group")
#     group_name = dialog_manager.dialog_data.get("selected_group_name")

#     dialog_manager.dialog_data['group_name'] = group_name

async def on_group_tasks_clicked(c, b, m: DialogManager, group_id: int):
    await m.start(
        TaskStates.LIST_TASKS,
        mode=StartMode.NORMAL,
        data={"context": "group",
              "group_id": group_id},
    )

# async def on_group_tasks(
#     callback: CallbackQuery,
#     widget: Select,
#     dialog_manager: DialogManager,
#     group_name: str,
# ):
#     dialog_manager.dialog_data["selected_group_name"] = group_name

#     groups = await service.get_all_groups()
#     selected_group = next((g for g in groups if g["name"] == group_name), None)

#     if selected_group:
#         dialog_manager.dialog_data["selected_group_name"] = selected_group["name"]

#     await dialog_manager.switch_to(OperatorGroupsStates.GROUP_TASKS)


async def on_group_select(callback: CallbackQuery,
                          widget: Select,
                          dialog_manager: DialogManager,
                          item_id: str,
                          ):
    dialog_manager.dialog_data["name"] = item_id
    groups = await service.get_all_groups()
    selected_group = next((g for g in groups if g["name"] == item_id), None)

    print("f: ", dialog_manager.dialog_data, dialog_manager.start_data, selected_group)

    if not selected_group:
        await callback.answer("❌ Группа не найден")
        return

    await dialog_manager.start(
        TaskStates.LIST_TASKS,
        mode=StartMode.NORMAL,
        data={
            "context": "group",
            "name": selected_group["name"],
            "id": selected_group["id"]
        },
    )


async def on_group_create(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager,
                          ):
    """Handle 'Create Group' button click - switch to group creation state"""
    from bot.modules.states import OperatorGroupCreateStates

    await dialog_manager.start(OperatorGroupCreateStates.CREATE_GROUP_NAME)


async def on_group_title_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle group title input and create group"""
    dialog_manager.dialog_data["group_title"] = data
    from bot.modules.states import OperatorGroupCreateStates
    await dialog_manager.switch_to(OperatorGroupCreateStates.CREATE_GROUP_DESCRIPTION)


async def on_group_description_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle group description input and create group"""
    dialog_manager.dialog_data["group_description"] = data
    from bot.modules.states import OperatorGroupCreateStates
    dialog_manager.switch_to(OperatorGroupCreateStates.CREATE_GROUP_CONFIRM)


async def on_confirm_group_creation(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Handle group creation confirmation"""
    group_title = dialog_manager.dialog_data.get("group_title")
    group_description = dialog_manager.dialog_data.get("group_description")

    print("DONE?")

    from src.modules.groups.schemes import GroupCreateRequest

    group_data = GroupCreateRequest(
        name=group_title,
        description=group_description,
    )

    created_group = await service.create_group(group_data)

    if created_group:
        await callback.answer("✅ Группа успешно создана.")
    else:
        await callback.answer("❌ Ошибка при создании группы. Попробуйте позже.")

    # Clear dialog data related to group creation
    dialog_manager.dialog_data.pop("group_title", None)
    dialog_manager.dialog_data.pop("group_description", None)

    # Return to groups list
    await dialog_manager.done()


async def on_page_next(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Go to next page of students"""
    current_page = dialog_manager.dialog_data.get("students_page", 0)
    dialog_manager.dialog_data["students_page"] = current_page + 1
    await callback.answer()


async def on_page_prev(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Go to previous page of students"""
    current_page = dialog_manager.dialog_data.get("students_page", 0)
    dialog_manager.dialog_data["students_page"] = max(0, current_page - 1)
    await callback.answer()


async def on_back_to_profile(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Go back to profile and clear sort"""
    # dialog_manager.dialog_data.pop("sort_by", None)  # Clear sort
    await dialog_manager.done()
