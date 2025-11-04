from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import MessageInput, ManagedTextInput
from datetime import datetime, timedelta
from typing import Dict, Any

from bot.modules.tasks.service import get_student_tasks, get_task_by_id, get_all_students
from bot.modules.start.service import get_user

router = Router()


# ============ STUDENT HANDLERS ============

async def get_student_tasks_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for student tasks list"""
    telegram_id = None
    
    if dialog_manager.event.from_user:
        telegram_id = dialog_manager.event.from_user.id
    
    if not telegram_id:
        return {"tasks": [], "tasks_count": 0, "sort_display": "По умолчанию"}
    
    # Get current sort type from dialog_data (default: None)
    sort_by = dialog_manager.dialog_data.get("sort_by", None)
    
    tasks = await get_student_tasks(telegram_id, sort_by=sort_by)
    
    # Add status emoji to each task
    status_emoji_map = {
        "pending": "⏳",
        "in_progress": "🔄",
        "completed": "✅",
        "overdue": "⚠️",
    }
    
    for task in tasks:
        status = task.get("status", "pending").lower()
        task["status_emoji"] = status_emoji_map.get(status, "❓")
    
    # Get current sort display name
    sort_display = {
        None: "По умолчанию",
        "start_time": "По дате начала ⬆️",
        "end_time": "По дедлайну ⬆️",
        "status": "По статусу ⬆️"
    }.get(sort_by, "По умолчанию")
    
    return {
        "tasks": tasks,
        "tasks_count": len(tasks),
        "sort_display": sort_display
    }


async def on_task_select(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    """Handle task selection - save task_id and switch to detail view"""
    dialog_manager.dialog_data["selected_task_id"] = item_id
    
    # Determine which state to go to based on current state
    from bot.modules.start.windows import StudentStates, OperatorStates
    
    current_state = dialog_manager.current_context().state
    
    if current_state == StudentStates.MY_TASKS:
        await dialog_manager.switch_to(StudentStates.TASK_DETAIL)
    elif current_state == OperatorStates.STUDENT_TASKS:
        await dialog_manager.switch_to(OperatorStates.TASK_DETAIL)


async def get_task_detail_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for task detail view"""
    task_id = dialog_manager.dialog_data.get("selected_task_id")
    
    if not task_id:
        return {
            "task": {
                "title": "Ошибка",
                "description": "Задача не найдена",
                "start_date": "—",
                "due_date": "—",
                "status_display": "—",
            },
            "student_name": "—",
        }
    
    task = await get_task_by_id(task_id)
    
    if not task:
        return {
            "task": {
                "title": "Ошибка",
                "description": "Задача не найдена",
                "start_date": "—",
                "due_date": "—",
                "status_display": "—",
            },
            "student_name": "—",
        }
    
    # Format dates
    start_date = task.get("start_date", "Не указано")
    due_date = task.get("due_date", "Не указано")
    
    if start_date and start_date != "Не указано":
        start_date = format_date(start_date)
    if due_date and due_date != "Не указано":
        due_date = format_date(due_date)
    
    # Status display
    status_display_map = {
        "pending": "⏳ Ожидает",
        "in_progress": "🔄 В работе",
        "completed": "✅ Завершено",
        "overdue": "⚠️ Просрочено",
    }
    
    status = task.get("status", "pending").lower()
    task["status_display"] = status_display_map.get(status, status.capitalize())
    task["start_date"] = start_date
    task["due_date"] = due_date
    
    # Get student name if operator is viewing
    student_name = dialog_manager.dialog_data.get("selected_student_name", "")
    
    return {
        "task": task,
        "student_name": student_name,
    }


async def on_back_to_profile(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Go back to profile and clear sort"""
    dialog_manager.dialog_data.pop("sort_by", None)  # Clear sort
    await dialog_manager.done()


# ============ OPERATOR HANDLERS ============

async def get_operator_students_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for operator students list with pagination"""
    # Get current page from dialog_data
    current_page = dialog_manager.dialog_data.get("students_page", 0)
    page_size = 5  # Max 5 students per page
    
    students = await get_all_students()
    total_students = len(students)
    total_pages = (total_students + page_size - 1) // page_size if total_students > 0 else 1
    
    # Calculate pagination
    start_idx = current_page * page_size
    end_idx = start_idx + page_size
    students_page = students[start_idx:end_idx]
    
    return {
        "students_page": students_page,
        "total_students": total_students,
        "current_page": current_page + 1,  # Display 1-indexed
        "total_pages": total_pages,
        "has_prev": current_page > 0,
        "has_next": current_page < total_pages - 1,
    }


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


async def on_student_select(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    """Handle student selection - save student_id and switch to their tasks"""
    dialog_manager.dialog_data["selected_student_telegram_id"] = int(item_id)
    
    # Get student info to save name
    students = await get_all_students()
    selected_student = next((s for s in students if str(s["telegram_id"]) == item_id), None)
    
    if selected_student:
        student_name = f"{selected_student['first_name']} {selected_student['last_name']}"
        dialog_manager.dialog_data["selected_student_name"] = student_name
    
    # Clear sort when selecting new student
    dialog_manager.dialog_data.pop("sort_by", None)
    
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.STUDENT_TASKS)


async def get_student_tasks_for_operator_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for operator viewing student's tasks"""
    student_telegram_id = dialog_manager.dialog_data.get("selected_student_telegram_id")
    student_name = dialog_manager.dialog_data.get("selected_student_name", "Неизвестный студент")

    dialog_manager.dialog_data["student_name"] = student_name

    if not student_telegram_id:
        return {
            "tasks": [],
            "tasks_count": 0,
            "student_name": student_name,
            "sort_display": "По умолчанию"
        }
    
    # Get current sort type
    sort_by = dialog_manager.dialog_data.get("sort_by", None)
    
    tasks = await get_student_tasks(student_telegram_id, sort_by=sort_by)
    
    # Add status emoji to each task
    status_emoji_map = {
        "pending": "⏳",
        "in_progress": "🔄",
        "completed": "✅",
        "overdue": "⚠️",
    }
    
    for task in tasks:
        status = task.get("status", "pending").lower()
        task["status_emoji"] = status_emoji_map.get(status, "❓")
    
    # Get current sort display name
    sort_display = {
        None: "По умолчанию",
        "start_time": "По дате начала ⬆️",
        "end_time": "По дедлайну ⬆️",
        "status": "По статусу ⬆️"
    }.get(sort_by, "По умолчанию")
    
    return {
        "tasks": tasks,
        "tasks_count": len(tasks),
        "student_name": student_name,
        "sort_display": sort_display
    }


async def get_create_task_confirm_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for task creation confirmation window"""
    student_name = dialog_manager.dialog_data.get("selected_student_name", "Неизвестный студент")
    
    return {
        "student_name": student_name,
    }


# ============ HELPER FUNCTIONS ============

def format_date(date_str: str) -> str:
    """Format date string to readable format"""
    if not date_str or date_str == "Не указано":
        return "Не указано"
    
    formats_to_try = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(date_str.split('+')[0].split('Z')[0], fmt)
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
    
    return date_str


# ============ TASK CREATION HANDLERS (FOR OPERATOR) ============

async def on_create_task_start(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Start task creation flow"""
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_TITLE)


async def on_task_title_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle task title input"""
    dialog_manager.dialog_data["task_title"] = data
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_DESCRIPTION)


async def on_task_description_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle task description input"""
    dialog_manager.dialog_data["task_description"] = data
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_START_DATE)


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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_DUE_DATE)


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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_CONFIRM)


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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_CONFIRM)
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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_CONFIRM)
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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_CONFIRM)
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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_CONFIRM)
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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_CONFIRM)
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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_CONFIRM)
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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_CONFIRM)
    await callback.answer(f"✅ Дедлайн: {due_date_str}")


async def on_no_due_date(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set no due date"""
    dialog_manager.dialog_data["task_due_date"] = "Не указано"
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.CREATE_TASK_CONFIRM)
    await callback.answer("✅ Дедлайн не установлен")


async def on_confirm_create_task(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Confirm and create task"""
    # Get data from dialog_data
    title = dialog_manager.dialog_data.get("task_title", "")
    description = dialog_manager.dialog_data.get("task_description", "")
    start_date = dialog_manager.dialog_data.get("task_start_date", "")
    due_date = dialog_manager.dialog_data.get("task_due_date", "Не указано")
    student_telegram_id = dialog_manager.dialog_data.get("selected_student_telegram_id")
    
    if not all([title, description, start_date, student_telegram_id]):
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
        from bot.modules.start.windows import OperatorStates
        await dialog_manager.switch_to(OperatorStates.STUDENT_TASKS)
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
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.STUDENT_TASKS)


def validate_date_format(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD or YYYY-MM-DD HH:MM"""
    try:
        # Try datetime format first
        datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        try:
            # Fallback to date only format
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False


def parse_datetime(date_str: str) -> datetime:
    """Parse datetime string to datetime object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        # If only date provided, set time to 00:00
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.replace(hour=0, minute=0)


# ============ SORT HANDLERS ============

async def on_sort_by_start_date(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Sort tasks by start date"""
    dialog_manager.dialog_data["sort_by"] = "start_time"
    await callback.answer("✅ Сортировка по дате начала")


async def on_sort_by_due_date(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Sort tasks by due date"""
    dialog_manager.dialog_data["sort_by"] = "end_time"
    await callback.answer("✅ Сортировка по дедлайну")


async def on_sort_by_status(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Sort tasks by status"""
    dialog_manager.dialog_data["sort_by"] = "status"
    await callback.answer("✅ Сортировка по статусу")


async def on_sort_reset(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Reset sort to default"""
    dialog_manager.dialog_data.pop("sort_by", None)
    await callback.answer("✅ Сортировка сброшена")
