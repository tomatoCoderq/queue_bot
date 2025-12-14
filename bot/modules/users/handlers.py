from typing import Any, Dict
from aiogram import Router
from aiogram_dialog import DialogManager
from html import escape


from bot.modules import states
from bot.modules import states

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select

from bot.modules.users import service as user_service
from loguru import logger

router = Router()


async def get_operator_students_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    students = await user_service.get_all_students()
    total_students = len(students)
    students = sorted(students, key=lambda x: x.get("first_name"))

    logger.info(f"Fetched {total_students} students for operator view")

    return {
        "students_page": students,
        "total_students": total_students,
    }


async def on_student_select(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    students = await user_service.get_all_students()
    selected_student = next(
        (s for s in students if str(s["telegram_id"]) == item_id), None)

    if not selected_student:
        logger.warning(f"Student with telegram_id {item_id} not found")
        await callback.answer("❌ Студент не найден")
        return

    student_name = f"{escape(selected_student['first_name'])} {escape(selected_student['last_name'])}"
    student_telegram_id = int(item_id)

    dialog_manager.dialog_data["selected_student_telegram_id"] = student_telegram_id
    dialog_manager.dialog_data["selected_student_name"] = student_name

    await dialog_manager.switch_to(states.OperatorStudentsStates.STUDENTS_INFO)


async def on_client_tasks(c, b, dialog_manager: DialogManager):
    """Handle client tasks button - show tasks for selected student"""
    student_telegram_id = dialog_manager.dialog_data.get(
        "selected_student_telegram_id")
    student_name = dialog_manager.dialog_data.get(
        "selected_student_name", "Неизвестный студент")

    await dialog_manager.start(
        states.OperatorTaskStates.LIST_TASKS,
        data={
            "context": "student_by_operator",
            "student_id": student_telegram_id,
            "student_name": student_name,
        }
    )


async def on_client_penalties(c, b, dialog_manager: DialogManager):
    await c.answer("🔧 Функция штрафов находится в процессе разработки.", show_alert=True)


async def on_client_details(c, b, dialog_manager: DialogManager):
    await c.answer("🔧 Функция принтов находится в процессе разработки.", show_alert=True)


async def getter_client_card(dialog_manager: DialogManager, **kwargs):
    '''return: name, tid, tasks, penalties'''
    to_return = {}
    selected_student_telegram_id = dialog_manager.dialog_data["selected_student_telegram_id"]

    client = await user_service.get_user_by_id(selected_student_telegram_id)
    logger.info(f"Fetching student card with selected id: {selected_student_telegram_id}")

    tasks = await user_service.get_student_tasks(selected_student_telegram_id)
    logger.info(f"Fetched {len(tasks)} tasks for student with id: {selected_student_telegram_id}")

    to_return["name"] = client["first_name"] + " " + client["last_name"]
    to_return["telegram_id"] = selected_student_telegram_id
    to_return["tasks"] = len(tasks)
    to_return["penalties"] = 0

    return to_return


async def on_delete_student_click(c, b, dialog_manager: DialogManager):
    """Switch to delete confirmation for the selected student"""
    if not dialog_manager.dialog_data.get("selected_student_telegram_id"):
        await c.answer("❌ Студент не выбран")
        return

    await dialog_manager.switch_to(states.OperatorStudentsStates.STUDENTS_DELETE_CONFIRM)


async def getter_delete_confirmation(dialog_manager: DialogManager, **kwargs):
    """Provide data for delete confirmation window"""
    return {
        "student_name": dialog_manager.dialog_data.get("selected_student_name", "Неизвестный студент"),
        "telegram_id": dialog_manager.dialog_data.get("selected_student_telegram_id"),
    }


async def on_confirm_delete_student(callback: CallbackQuery, button, dialog_manager: DialogManager):
    student_telegram_id = dialog_manager.dialog_data.get("selected_student_telegram_id")
    student_name = dialog_manager.dialog_data.get("selected_student_name", "Студент")

    if not student_telegram_id:
        await callback.answer("❌ Студент не выбран")
        return

    success = await user_service.delete_student(student_telegram_id)

    if success:
        logger.info(f"Deleted student with telegram_id {student_telegram_id}")
        bot_instance = callback.message.bot

        try:
            await bot_instance.send_message(
                chat_id=student_telegram_id,
                text=(
                    "🗑️ <b>Аккаунт удален</b>\n\n"
                    f"👤 <b>{escape(student_name)}</b>\n\n"
                    "Ваш аккаунт был удален оператором."
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning(f"Failed to notify student {student_telegram_id} about deletion: {e}")
            
        await callback.answer("✅ Студент удален")
        
        dialog_manager.dialog_data.pop("selected_student_telegram_id", None)
        dialog_manager.dialog_data.pop("selected_student_name", None)
        
        await dialog_manager.done()
        # await dialog_manager.start(states.OperatorStudentsStates.STUDENTS_LIST)
    else:
        await callback.answer("❌ Ошибка при удалении студента", show_alert=True)


async def on_update_student_click(c, b, dialog_manager: DialogManager):
    """Switch to update user state for the selected student"""
    if not dialog_manager.dialog_data.get("selected_student_telegram_id"):
        await c.answer("❌ Студент не выбран")
        return

    await dialog_manager.start(
        states.OperatorUpdateUserStates.UPDATE_USER_ROLE,
        data={
            "selected_student_telegram_id": dialog_manager.dialog_data.get("selected_student_telegram_id"),
            "selected_student_name": dialog_manager.dialog_data.get("selected_student_name"),
        }
    )


async def on_role_select(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Handle role selection for update"""
    dialog_manager.dialog_data["update_role"] = item_id
    await dialog_manager.switch_to(states.OperatorUpdateUserStates.UPDATE_USER_FIRST_NAME)
    await callback.answer()


async def on_update_first_name(message, widget, dialog_manager: DialogManager, data: str):
    """Handle first name input for update"""
    dialog_manager.dialog_data["update_first_name"] = data
    from bot.modules.states import OperatorUpdateUserStates
    await dialog_manager.switch_to(OperatorUpdateUserStates.UPDATE_USER_LAST_NAME)


async def on_update_last_name(message, widget, dialog_manager: DialogManager, data: str):
    """Handle last name input for update"""
    dialog_manager.dialog_data["update_last_name"] = data
    from bot.modules.states import OperatorUpdateUserStates
    await dialog_manager.switch_to(OperatorUpdateUserStates.UPDATE_USER_CONFIRM)


async def getter_update_confirmation(dialog_manager: DialogManager, **kwargs):
    """Provide data for update confirmation window"""
    return {
        "student_name": dialog_manager.start_data.get("selected_student_name", "Неизвестный студент"),
        "new_role": dialog_manager.dialog_data.get("update_role", "Не изменяется"),
        "new_first_name": dialog_manager.dialog_data.get("update_first_name", "Не изменяется"),
        "new_last_name": dialog_manager.dialog_data.get("update_last_name", "Не изменяется"),
    }


async def on_confirm_update_user(callback: CallbackQuery, button, dialog_manager: DialogManager):
    """Confirm user update and send to API"""
    student_telegram_id = dialog_manager.start_data.get("selected_student_telegram_id")
    update_role = dialog_manager.dialog_data.get("update_role")
    update_first_name = dialog_manager.dialog_data.get("update_first_name")
    update_last_name = dialog_manager.dialog_data.get("update_last_name")

    if not student_telegram_id:
        await callback.answer("❌ Студент не выбран")
        return
    
    # Check if at least one field was filled
    if not any([update_role, update_first_name, update_last_name]):
        await callback.answer("ℹ️ Ни одно поле не было изменено", show_alert=True)
        
        dialog_manager.dialog_data.pop("update_role", None)
        dialog_manager.dialog_data.pop("update_first_name", None)
        dialog_manager.dialog_data.pop("update_last_name", None)
        await dialog_manager.done()
        return

    success = await user_service.update_user(
        student_telegram_id,
        role=update_role,
        first_name=update_first_name,
        last_name=update_last_name
    )

    if success:
        logger.info(f"Updated user {student_telegram_id}")
        await callback.answer("✅ Данные студента обновлены")
        # Clear update data
        dialog_manager.dialog_data.pop("update_role", None)
        dialog_manager.dialog_data.pop("update_first_name", None)
        dialog_manager.dialog_data.pop("update_last_name", None)
        # Return to student card
        await dialog_manager.done()
    else:
        await callback.answer("❌ Ошибка при обновлении данных", show_alert=True)
