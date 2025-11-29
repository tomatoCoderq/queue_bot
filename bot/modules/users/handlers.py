
        # on_client_tasks,
        # on_client_penalties,
        # on_client_details,
        # getter_client_card
        
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

router = Router()


async def get_operator_students_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for operator students list with pagination"""
    # Get current page from dialog_data
    current_page = dialog_manager.dialog_data.get("students_page", 0)
    page_size = 5  # Max 5 students per page

    students = await user_service.get_all_students()
    total_students = len(students)
    total_pages = (total_students + page_size -
                   1) // page_size if total_students > 0 else 1

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
        await callback.answer("❌ Студент не найден")
        return

    student_name = f"{escape(selected_student['first_name'])} {escape(selected_student['last_name'])}"
    student_telegram_id = int(item_id)

    from aiogram_dialog import StartMode

    dialog_manager.dialog_data["selected_student_telegram_id"] = student_telegram_id
    dialog_manager.dialog_data["selected_student_name"] = student_name

    await dialog_manager.switch_to(states.OperatorStudentsStates.STUDENTS_INFO)

    # await dialog_manager.start(
    #     TaskStates.LIST_TASKS,
    #     mode=StartMode.NORMAL,
    #     data={
    #         "context": "student_by_operator",
    #         "student_id": student_telegram_id,
    #         "student_name": student_name,
    #     },
    # )

async def on_client_tasks(c, b, dialog_manager: DialogManager):
    """Handle client tasks button - show tasks for selected student"""
    student_telegram_id = dialog_manager.dialog_data.get("selected_student_telegram_id")
    student_name = dialog_manager.dialog_data.get("selected_student_name", "Неизвестный студент")
    
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
    
    print(dialog_manager.start_data, dialog_manager.dialog_data)
    
    client = await user_service.get_user_by_id(selected_student_telegram_id)
    print(client)
    
    tasks = await user_service.get_student_tasks(selected_student_telegram_id)
    print(tasks)
    
    to_return["name"] = client["first_name"] + " " + client["last_name"]
    to_return["telegram_id"] = selected_student_telegram_id
    to_return["tasks"] = len(tasks)
    to_return["penalties"] = 0
    
    return to_return
    
    
    
    
