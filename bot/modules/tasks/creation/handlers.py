from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import MessageInput, ManagedTextInput
from datetime import datetime, timedelta
from typing import Dict, Any

from bot.modules.states import OperatorTaskStates as TaskStates
from bot.modules.tasks import service as tasks_service
from bot.modules.users import service as user_service
from bot.modules.groups import service as groups_service



async def on_create_task_start(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Start task creation flow"""
    from bot.modules.states import OperatorTaskCreateStates
    print("D: ", dialog_manager.dialog_data, dialog_manager.start_data)
    
    await dialog_manager.start(OperatorTaskCreateStates.CREATE_TASK_TITLE, data=dialog_manager.start_data)


async def on_task_title_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle task title input"""
    dialog_manager.dialog_data["task_title"] = data
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_DESCRIPTION)


async def on_task_description_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle task description input"""
    dialog_manager.dialog_data["task_description"] = data
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_START_DATE)


async def on_task_start_date_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle task start date input"""
    # Validate date format
    if not validate_date_format(data):
        await message.answer("❌ Неверный формат. Используйте YYYY-MM-DD HH:MM (например: 2025-11-05 14:30)\nИли просто YYYY-MM-DD (например: 2025-11-05)")
        return
    
    dialog_manager.dialog_data["task_start_date"] = data
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_DUE_DATE)


async def on_task_due_date_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle task due date input"""
    # Validate date format
    if not validate_date_format(data):
        await message.answer("❌ Неверный формат. Используйте YYYY-MM-DD HH:MM (например: 2025-11-15 18:00)\nИли просто YYYY-MM-DD (например: 2025-11-15)")
        return
    
    # Validate: due date should be after start date
    start_date_str = dialog_manager.dialog_data.get("task_start_date")
    if start_date_str:
        start_dt = parse_datetime(start_date_str)
        due_dt = parse_datetime(data)
        if due_dt <= start_dt:
            await message.answer("❌ Дедлайн должен быть позже даты начала")
            return
    
    dialog_manager.dialog_data["task_due_date"] = data
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)


# ============ QUICK DUE DATE HANDLERS ============

async def on_due_date_30min(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set due date to +30 minutes from start date"""
    start_date_str = dialog_manager.dialog_data.get("task_start_date")
    if not start_date_str:
        await callback.answer("❌ Ошибка: дата начала не установлена")
        return
    
    start_dt = parse_datetime(start_date_str)
    due_dt = start_dt + timedelta(minutes=30)
    due_date_str = due_dt.strftime("%Y-%m-%d %H:%M")
    
    dialog_manager.dialog_data["task_due_date"] = due_date_str
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)
    await callback.answer(f"✅ Дедлайн: {due_date_str}")


async def on_due_date_45min(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set due date to +45 minutes from start date"""
    start_date_str = dialog_manager.dialog_data.get("task_start_date")
    if not start_date_str:
        await callback.answer("❌ Ошибка: дата начала не установлена")
        return
    
    start_dt = parse_datetime(start_date_str)
    due_dt = start_dt + timedelta(minutes=45)
    due_date_str = due_dt.strftime("%Y-%m-%d %H:%M")
    
    dialog_manager.dialog_data["task_due_date"] = due_date_str
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)
    await callback.answer(f"✅ Дедлайн: {due_date_str}")


async def on_due_date_1hour(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set due date to +1 hour from start date"""
    start_date_str = dialog_manager.dialog_data.get("task_start_date")
    if not start_date_str:
        await callback.answer("❌ Ошибка: дата начала не установлена")
        return
    
    start_dt = parse_datetime(start_date_str)
    due_dt = start_dt + timedelta(hours=1)
    due_date_str = due_dt.strftime("%Y-%m-%d %H:%M")
    
    dialog_manager.dialog_data["task_due_date"] = due_date_str
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)
    await callback.answer(f"✅ Дедлайн: {due_date_str}")


async def on_due_date_2hours(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set due date to +2 hours from start date"""
    start_date_str = dialog_manager.dialog_data.get("task_start_date")
    if not start_date_str:
        await callback.answer("❌ Ошибка: дата начала не установлена")
        return
    
    start_dt = parse_datetime(start_date_str)
    due_dt = start_dt + timedelta(hours=2)
    due_date_str = due_dt.strftime("%Y-%m-%d %H:%M")
    
    dialog_manager.dialog_data["task_due_date"] = due_date_str
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)
    await callback.answer(f"✅ Дедлайн: {due_date_str}")


async def on_due_date_4hours(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set due date to +4 hours from start date"""
    start_date_str = dialog_manager.dialog_data.get("task_start_date")
    if not start_date_str:
        await callback.answer("❌ Ошибка: дата начала не установлена")
        return
    
    start_dt = parse_datetime(start_date_str)
    due_dt = start_dt + timedelta(hours=4)
    due_date_str = due_dt.strftime("%Y-%m-%d %H:%M")
    
    dialog_manager.dialog_data["task_due_date"] = due_date_str
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)
    await callback.answer(f"✅ Дедлайн: {due_date_str}")


async def on_due_date_8hours(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set due date to +8 hours from start date"""
    start_date_str = dialog_manager.dialog_data.get("task_start_date")
    if not start_date_str:
        await callback.answer("❌ Ошибка: дата начала не установлена")
        return
    
    start_dt = parse_datetime(start_date_str)
    due_dt = start_dt + timedelta(hours=8)
    due_date_str = due_dt.strftime("%Y-%m-%d %H:%M")
    
    dialog_manager.dialog_data["task_due_date"] = due_date_str
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)
    await callback.answer(f"✅ Дедлайн: {due_date_str}")


async def on_due_date_1day(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set due date to +1 day from start date"""
    start_date_str = dialog_manager.dialog_data.get("task_start_date")
    if not start_date_str:
        await callback.answer("❌ Ошибка: дата начала не установлена")
        return
    
    start_dt = parse_datetime(start_date_str)
    due_dt = start_dt + timedelta(days=1)
    due_date_str = due_dt.strftime("%Y-%m-%d %H:%M")
    
    dialog_manager.dialog_data["task_due_date"] = due_date_str
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)
    await callback.answer(f"✅ Дедлайн: {due_date_str}")


async def on_no_due_date(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set no due date"""
    dialog_manager.dialog_data["task_due_date"] = "Не указано"
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)
    await callback.answer("✅ Дедлайн не установлен")


async def on_confirm_create_task(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Confirm and create task"""
    # Get data from dialog_data
    print("DIALOG_DATA:", dialog_manager.dialog_data)
    title = dialog_manager.dialog_data.get("task_title", "")
    description = dialog_manager.dialog_data.get("task_description", "")
    start_date = dialog_manager.dialog_data.get("task_start_date", "")
    due_date = dialog_manager.dialog_data.get("task_due_date", "Не указано")
    student_telegram_id = dialog_manager.start_data.get("student_id")

    print("telegram: ", student_telegram_id)
    print(dialog_manager.start_data)

    if not all([title, description, start_date, student_telegram_id]):
        print([title, description, start_date, student_telegram_id])
        await callback.answer("❌ Ошибка: отсутствуют данные")
        return
    
    # Type check for student_telegram_id
    if not isinstance(student_telegram_id, int):
        await callback.answer("❌ Ошибка: некорректный ID студента")
        return
    
    # Create and assign task
    from bot.modules.tasks.service import create_task_and_assign
    
    task = await create_task_and_assign(
        title=title,
        description=description,
        start_date=start_date,
        due_date=due_date if due_date != "Не указано" else None,
        student_telegram_id=student_telegram_id,
    )
    
    if task:
        await callback.answer("✅ Задача успешно создана и назначена студенту!")
        # Clear task creation data
        dialog_manager.dialog_data.pop("task_title", None)
        dialog_manager.dialog_data.pop("task_description", None)
        dialog_manager.dialog_data.pop("task_start_date", None)
        dialog_manager.dialog_data.pop("task_due_date", None)
        # Return to student tasks list
        from bot.modules.states import OperatorStudentsStates
        await dialog_manager.done()
    else:
        await callback.answer("❌ Ошибка при создании задачи. Попробуйте позже.")

# TODO: Now cancel doesn't work and just return task creation page with error
async def on_cancel_create_task(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Cancel task creation"""
    # Clear task creation data
    dialog_manager.dialog_data.pop("task_title", None)
    dialog_manager.dialog_data.pop("task_description", None)
    dialog_manager.dialog_data.pop("task_start_date", None)
    dialog_manager.dialog_data.pop("task_due_date", None)
    
    await callback.answer("❌ Создание задачи отменено")
    from bot.modules.states import OperatorStudentsStates
    await dialog_manager.done()