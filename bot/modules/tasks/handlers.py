from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import MessageInput
from datetime import datetime
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
        return {"tasks": [], "tasks_count": 0}
    
    tasks = await get_student_tasks(telegram_id)
    
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
    
    return {
        "tasks": tasks,
        "tasks_count": len(tasks),
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
    """Go back to profile"""
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
    
    from bot.modules.start.windows import OperatorStates
    await dialog_manager.switch_to(OperatorStates.STUDENT_TASKS)


async def get_student_tasks_for_operator_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for operator viewing student's tasks"""
    student_telegram_id = dialog_manager.dialog_data.get("selected_student_telegram_id")
    student_name = dialog_manager.dialog_data.get("selected_student_name", "Неизвестный студент")
    
    if not student_telegram_id:
        return {
            "tasks": [],
            "tasks_count": 0,
            "student_name": student_name,
        }
    
    tasks = await get_student_tasks(student_telegram_id)
    
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
    
    return {
        "tasks": tasks,
        "tasks_count": len(tasks),
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
