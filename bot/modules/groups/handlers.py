from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput
from typing import Dict, Any


from bot.modules.groups import service

from bot.modules.states import OperatorGroupsStates, OperatorTaskStates as TaskStates

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

async def on_group_tasks_clicked(c, b, m: DialogManager):
    
    await m.start(
        TaskStates.LIST_TASKS,
        mode=StartMode.NORMAL,
        data={"context": "group",
              "name": m.dialog_data.get("selected_group").get("name"),
              "id": m.dialog_data.get("selected_group").get("id"),},
    )

async def on_add_user_group(c, w, m: DialogManager):
    """Handle 'Add User to Group' button click - switch to add user state"""
    await m.switch_to(OperatorGroupsStates.GROUP_ADD_USER)

async def on_add_specific_user(callback: CallbackQuery,
                          widget: Select,
                          dialog_manager: DialogManager,
                          item_id: str,
                          ):
    print(dialog_manager.dialog_data, dialog_manager.start_data)
    group = dialog_manager.dialog_data.get("selected_group")
    if not group:
        await callback.answer("❌ Группа не найдена")
        return
    
    success = await service.add_student_to_group(group["id"], item_id)
    if success:
        await callback.answer("✅ Участник успешно добавлен в группу.")
    else:
        await callback.answer("❌ Ошибка при добавлении участника. Попробуйте позже.")
        
        
async def getter_group_clients(dialog_manager: DialogManager, **kwargs):
    group_id = dialog_manager.dialog_data["selected_group"]["id"]

    clients = await service.get_group_clients(group_id)

    print("Clients: ", clients)
    
    lines = []
    for i, c in enumerate(clients):
        lines.append(f"{i+1}. {c['first_name']} {c['last_name']}")
    students_text = "\n".join(lines) if lines else "В группе нет участников"

    return {"students_text": students_text}


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
    dialog_manager.dialog_data["selected_group"] = selected_group

    await dialog_manager.switch_to(OperatorGroupsStates.GROUP_ACTIONS)


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

async def getter_client_group_info(dialog_manager: DialogManager, **kwargs):
    print(dialog_manager.dialog_data, dialog_manager.start_data)
    # user = await user_service.get_user_by_id(dialog_manager.start_data.get("telegram_id"))
    
    group_id = await service.get_client_group(dialog_manager.start_data.get("telegram_id"))
    group = await service.get_group_by_id(group_id)
    
    print("Group info:", group)
    
    if not group:
        return {"group_name": "Группа не найдена", "group_description": ""}

    return {
        "name": group.name,
        "description": group.description if hasattr(group, "description") and group.description else "Описание отсутствует",
    }