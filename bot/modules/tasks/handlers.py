import html
from aiogram import Router
from aiogram.types import CallbackQuery, Message, InputMediaDocument, InputMediaPhoto
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from datetime import datetime, time, timedelta, timezone

from typing import Dict, Any
from html import escape
from loguru import logger


from bot.modules.states import OperatorTaskStates as TaskStates
from bot.modules.tasks import service as tasks_service
from bot.modules.users import service as user_service
from bot.modules.groups import service as groups_service
from bot.modules.files import service as files_service


router = Router()


async def tasks_list_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    start_data = dialog_manager.start_data
    logger.info(f"Dialog data: {dialog_manager.dialog_data}")
    logger.info(f"Start data: {dialog_manager.start_data}")

    context = start_data.get("context")

    if not context:
        raise ValueError("No context given")

    logger.info(f"Start data: {start_data}")

    sort_by = dialog_manager.dialog_data.get("sort_by", None)
    show_completed = dialog_manager.dialog_data.get("show_completed", False)

    status_emoji_map = {
        "pending": "⏳",
        "in_progress": "🔄",
        "submitted": "📝",
        "completed": "✅",
        "rejected": "❌",
        "overdue": "⚠️",
    }

    tasks = []
    header = ""
    student_name = None
    group_name = None

    # Student checks his own tasks
    if context == "student_self":
        telegram_id = dialog_manager.event.from_user.id
        if not telegram_id:
            raise ValueError("No telegram_id in event")

        all_tasks = await user_service.get_student_tasks(telegram_id, sort_by=sort_by)
        tasks = all_tasks

        logger.info(f"All tasks for student: {len(all_tasks)}")

        header = "📚 Мои задачи"

    # Operator checks tasks of a specific student
    elif context == "student_by_operator":
        student_telegram_id = start_data.get("student_id")
        student_name = start_data.get("student_name", "Неизвестный студент")

        all_tasks = await user_service.get_student_tasks(student_telegram_id, sort_by=sort_by)

        logger.info(f"All tasks for student by operator: {len(all_tasks)}")

        tasks = all_tasks
        header = f" Задачи студента: {escape(student_name)}"

    # === 3. Оператор смотрит задачи группы ===
    elif context == "group" or context == "group_client":
        # group_id = start_data.get("group_id")
        group_name = start_data.get("name")
        group: groups_service.GroupReadResponse | None = await groups_service.get_group_by_name(group_name)

        group_id = start_data.get("id")
        all_tasks = await groups_service.get_group_tasks(group_id)

        logger.info(f"All tasks for group by operator: {len(all_tasks)}")

        tasks = all_tasks
        header = f"👥 Задачи группы: {escape(group_name) if group_name else 'Неизвестная группа'}"

    # elif context == "group_client":
    #     pass
    # фильтрация completed (актуально для студента, но пусть будет везде)
    if not show_completed:
        tasks = [t for t in tasks if t.get(
            "status", "").lower() != "completed"]

    completed_count = sum(1 for t in all_tasks if t.get(
        "status", "").lower() == "completed")

    for t in tasks:
        status = t.get("status", "pending").lower()
        t["status_emoji"] = status_emoji_map.get(status, "❓")

    sort_display = {
        None: "По умолчанию",
        "start_time": "По дате начала ⬆️",
        "end_time": "По дедлайну ⬆️",
        "status": "По статусу ⬆️",
    }.get(sort_by, "По умолчанию")

    toggle_button_text = "👁 Скрыть выполненные" if show_completed else "👁 Показать выполненные"

    return {
        "tasks": tasks,
        "tasks_count": len(tasks),
        "can_create_task": context in ("group", "student_by_operator"),
        "completed_count": completed_count,
        "total_count": len(all_tasks),
        "sort_display": sort_display,
        "show_completed": show_completed,
        "toggle_button_text": toggle_button_text,
        "header": header,
        "student_name": student_name,
        "group_name": group_name,
    }


async def task_detail_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    start_data = dialog_manager.start_data
    logger.debug(f"Found task_id in start_data: {start_data}, dialog_data: {dialog_manager.dialog_data}")
    context = start_data.get("context", "student_self")

    task_id = start_data.get("task_id")
    logger.debug(f"Task ID: {task_id}")
    if not task_id:
        return {}

    task = await tasks_service.get_task_by_id(task_id)
    if not task:
        return {}

    start_date = task.get("start_date", "Не указано")
    due_date = task.get("due_date", "Не указано")

    if start_date and start_date != "Не указано":
        start_date = format_date(start_date)
    if due_date and due_date != "Не указано":
        due_date = format_date(due_date)

    status_display_map = {
        "pending": "⏳ Ожидает",
        "in_progress": "🔄 В работе",
        "submitted": "📝 На проверке",
        "completed": "✅ Завершено",
        "rejected": "❌ Отклонено",
        "overdue": "⚠️ Просрочено",
    }
    status = task.get("status", "pending").lower()
    task["status_display"] = status_display_map.get(
        status, status.capitalize())
    task["start_date"] = start_date
    task["due_date"] = due_date
    task["has_rejection"] = bool(task.get("rejection_comment"))
    task["rejection_comment"] = task.get("rejection_comment", "")

    is_overdue = status == "overdue"
    overdue_warning = ""
    if is_overdue:
        overdue_warning = (
            "\n\n⚠️ <b>ВНИМАНИЕ: Задача просрочена!</b>\n"
            "Дедлайн уже прошел. Завершите задачу как можно скорее."
        )

    can_submit = status in ["pending", "in_progress", "rejected", "overdue"]

    # имя студента – для операторских сценариев
    student_name = None
    if context in ("student_by_operator", "group"):
        student_id = task.get("student_id")
        if student_id:
            student = await user_service.get_user(student_id)
            if student:
                student_name = f"{escape(student.get('first_name', ''))} {escape(student.get('last_name', ''))}"

    # Адаптивный текст кнопки "Назад"
    back_text_map = {
        "student_self": "К моим задачам",
        "student_by_operator": "К задачам студента",
        "group": "К задачам группы"
    }
    back_text = back_text_map.get(context, "К списку задач")

    return {
        "task": task,
        "student_name": student_name,
        "operator": context in ("student_by_operator", "group"),
        "can_submit": can_submit if context == "student_self" else False,
        "is_overdue": is_overdue,
        "overdue_warning": overdue_warning,
        "context": context,
        "back_text": back_text,
    }


async def on_task_select(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    dialog_manager.dialog_data["selected_task_id"] = item_id
    dialog_manager.start_data["task_id"] = item_id
    logger.debug(f"Start data: {dialog_manager.start_data}")
    await dialog_manager.start(TaskStates.DETAIL, data=dialog_manager.start_data)


async def on_back_to_profile(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Go back to profile and clear sort"""
    dialog_manager.dialog_data.pop("sort_by", None)  # Clear sort
    await dialog_manager.done()


async def on_delete_task(c, b, dialog_manager: DialogManager):
    task_id = dialog_manager.start_data.get("task_id")
    if not task_id:
        await c.answer("❌ Ошибка: задача не найдена")
        return

    success = await tasks_service.delete_task(task_id)

    if success:
        await c.answer("✅ Задача успешно удалена")
        await dialog_manager.done()  # Go back after deletion
    else:
        await c.answer("❌ Ошибка при удалении задачи")


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
    """Getter for task creation confirmation window"""
    student_name = dialog_manager.dialog_data.get(
        "selected_student_name", "Неизвестный студент")

    return {
        "student_name": student_name,
    }


def format_date(date_str: str) -> str:
    """Format date string to readable format with time (+3 hours timezone adjustment)"""
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
            # Add 3 hours for timezone adjustment (UTC+3)
            dt = dt + timedelta(hours=3)
            # Include time if it's present in the format
            if 'H' in fmt:
                return dt.strftime("%d.%m.%Y %H:%M")
            else:
                return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue

    return date_str


async def on_create_task_start(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Start task creation flow"""
    from bot.modules.states import OperatorTaskCreateStates
    logger.debug(f"Dialog data: {dialog_manager.dialog_data}, Start data: {dialog_manager.start_data}")

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


# ============ QUICK START DATE HANDLERS ============

async def on_start_date_now(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Установить время начала - сейчас"""
    from bot.modules.states import OperatorTaskCreateStates

    now = datetime.now(timezone.utc)
    # dialog_manager.dialog_data["task_start_date_raw"] = now

    start_date = (now + timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M")
    dialog_manager.dialog_data["task_start_date"] = start_date
    
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_DUE_DATE)
    await callback.answer(f"⏰ Время начала: {start_date}")


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

    due_dt = parse_datetime(data) - timedelta(hours=3)

    dialog_manager.dialog_data["task_due_date"] = due_dt.strftime("%Y-%m-%d %H:%M")
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_WAIT_PHOTOS)


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
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_WAIT_PHOTOS)
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
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_WAIT_PHOTOS)
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
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_WAIT_PHOTOS)
    await callback.answer(f"✅ Дедлайн: {due_date_str}")


async def on_no_due_date(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Set no due date"""
    dialog_manager.dialog_data["task_due_date"] = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M")
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_WAIT_PHOTOS)
    await callback.answer("✅ Дедлайн не установлен")


async def on_add_file(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Переход в состояние ожидания файла от пользователя"""
    from bot.modules.states import OperatorTaskCreateStates
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_ADD_PHOTO)
    await callback.answer("📎 Отправьте файл (фото или документ)")


async def on_file_received(
    message: Message,
    message_input: MessageInput,
    dialog_manager: DialogManager,
):
    """Обработка полученного файла (фото или документ)"""
    # Инициализируем список файлов если его нет
    if "pending_files" not in dialog_manager.dialog_data:
        dialog_manager.dialog_data["pending_files"] = []

    file_info = None

    if message.photo:
        photo = message.photo[-1]
        file_info = {
            "type": "photo",
            "name": f"photo_{len(dialog_manager.dialog_data['pending_files']) + 1}.jpg",
            "file_id": photo.file_id,
            "file_size": photo.file_size
        }
    elif message.document:
        doc = message.document
        file_info = {
            "type": "document",
            "name": doc.file_name or f"document_{len(dialog_manager.dialog_data['pending_files']) + 1}",
            "file_id": doc.file_id,
            "file_size": doc.file_size
        }

    logger.debug(f"File info: {file_info}")

    if file_info:
        # Просто сохраняем информацию о файле, не загружаем пока через API
        dialog_manager.dialog_data["pending_files"].append(file_info)

        files_count = len(dialog_manager.dialog_data["pending_files"])

        # Возвращаемся в состояние ожидания файлов
        from bot.modules.states import OperatorTaskCreateStates
        await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_WAIT_PHOTOS)

        await message.answer(f"✅ Файл добавлен: {file_info['name']}\n📎 Всего файлов: {files_count}")
    else:
        await message.answer("❌ Поддерживаются только фото и документы")


async def on_proceed_all_files_added(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Переход к подтверждению создания задачи (файлы будут загружены при создании задачи)"""
    from bot.modules.states import OperatorTaskCreateStates

    # Просто переходим к подтверждению, файлы загрузим при создании задачи с task_id
    await dialog_manager.switch_to(OperatorTaskCreateStates.CREATE_TASK_CONFIRM)
    
    parsed_start_date = parse_datetime(dialog_manager.dialog_data["task_start_date"])
    dialog_manager.dialog_data["show_start_date"] = (parsed_start_date + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")
    
    parsed_due_date = parse_datetime(dialog_manager.dialog_data["task_due_date"])
    dialog_manager.dialog_data["show_due_date"] = (parsed_due_date + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")
    
    await callback.answer("➡️ Переход к подтверждению задачи")


async def get_files_data(dialog_manager: DialogManager, **kwargs):
    pending_files = dialog_manager.dialog_data.get("pending_files", [])
    files_count = len(pending_files)

    if files_count == 0:
        files_info = "Файлы не добавлены"
    else:
        files_list = []
        for i, file in enumerate(pending_files, 1):
            file_type_emoji = "🖼️" if file["type"] == "photo" else "📄"
            # Экранируем HTML-символы в именах файлах
            safe_name = html.escape(file["name"])
            files_list.append(f"{i}. {file_type_emoji} {safe_name}")
        files_info = "\n".join(files_list)

    return {
        "files_count": files_count,
        "files_info": files_info,
        "has_files": files_count > 0
    }


async def on_confirm_create_task(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Confirm and create task"""
    # Get data from dialog_data
    logger.debug(f"Dialog data: {dialog_manager.dialog_data}")
    title = dialog_manager.dialog_data.get("task_title", "")
    description = dialog_manager.dialog_data.get("task_description", "")
    start_date = dialog_manager.dialog_data.get("task_start_date", "")
    due_date = dialog_manager.dialog_data.get("task_due_date", "")

    logger.debug(f"Start date: {start_date}")

    obj_id: str
    current_context = dialog_manager.start_data.get("context")

    if current_context == "group":
        obj_id = dialog_manager.start_data.get("id")

    elif current_context == "student_by_operator":
        obj_id = dialog_manager.start_data.get("student_id")

    else:
        await callback.answer("❌ Ошибка: неверный контекст создания задачи")
        return

    logger.debug(f"Start data: {dialog_manager.start_data}")

    if not all([title, description, start_date, obj_id]):
        logger.debug(f"Missing data - title: {title}, description: {description}, start_date: {start_date}, obj_id: {obj_id}")
        await callback.answer("❌ Ошибка: отсутствуют данные")
        return

    # Create and assign task
    from bot.modules.tasks.service import create_task_and_assign, create_and_add_task_group

    task: Dict[str, Any] | None = None
    if current_context == "group":
        task = await create_and_add_task_group(
            group_id=obj_id,
            title=title,
            description=description,
            start_date=start_date,
            due_date=due_date,
        )
        logger.debug(f"Created task for group: {task}")

    if current_context == "student_by_operator":
        logger.debug(f"Creating task with dates - start: {start_date} ({type(start_date)}), due: {due_date} ({type(due_date)})")
        task = await create_task_and_assign(
            title=title,
            description=description,
            start_date=start_date,
            due_date=due_date,
            student_telegram_id=obj_id,
        )

    logger.debug(f"Created task: {task}")

    if task:
        task_id = task.get("id")
        pending_files = dialog_manager.dialog_data.get("pending_files", [])

        # Загружаем файлы с task_id сразу после создания задачи
        if pending_files and task_id:
            try:
                uploaded_count = 0
                for file_info in pending_files:
                    # Получаем файл из Telegram
                    telegram_file = await callback.bot.get_file(file_info["file_id"])
                    file_data = await callback.bot.download_file(telegram_file.file_path)

                    # Читаем содержимое файла
                    file_bytes = file_data.read()

                    # Загружаем файл с привязкой к задаче
                    logger.debug(f"Uploading file type: {file_info['type']}")
                    uploaded_file = await files_service.upload_file(
                        file_data=file_bytes,
                        filename=file_info["name"],
                        file_type=file_info["type"],
                        task_id=task_id,
                        file_id=file_info["file_id"]
                    )

                    logger.debug(f"File uploaded: {uploaded_file}")

                    if uploaded_file:
                        uploaded_count += 1
                    else:
                        logger.error(f"Error uploading file: {file_info['name']}")

                logger.info(f"Uploaded {uploaded_count} files for task {task_id}")
            except Exception as e:
                logger.error(f"Error uploading files: {e}")

        await callback.answer("✅ Задача успешно создана и назначена студенту!")
        # Clear task creation data
        dialog_manager.dialog_data.pop("task_title", None)
        dialog_manager.dialog_data.pop("task_description", None)
        dialog_manager.dialog_data.pop("task_start_date", None)
        dialog_manager.dialog_data.pop("task_due_date", None)
        dialog_manager.dialog_data.pop("pending_files", None)
        # Return to student tasks list
        await dialog_manager.done()
    else:
        await callback.answer("❌ Ошибка при создании задачи. Попробуйте позже.")


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

    # Очищаем pending_files (они еще не загружены в API)
    pending_files = dialog_manager.dialog_data.pop("pending_files", [])
    if pending_files:
        logger.debug(f"Cleared {len(pending_files)} unsent files")

    await callback.answer("❌ Создание задачи отменено")
    await dialog_manager.done()


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


async def on_view_task_files(c, b, dialog_manager: DialogManager):
    """Handle viewing task files"""

    from aiogram_dialog.api.entities import ShowMode

    task_id = dialog_manager.start_data.get("task_id")
    if not task_id:
        await c.answer("❌ Ошибка: задача не найдена")
        return

    files = await files_service.get_task_files(task_id)

    if not files:
        await c.answer("ℹ️ Файлы не найдены")
        return

    albume_docs = []
    albume_photos = []
    for file in files:
        file_type = file.get("type", "document")
        file_name = file.get("filename", "file")
        file_id = file.get("file_id")

        logger.debug(f"File metadata - name: {file_name}, type: {file_type}, id: {file_id}")

        if file_type == "photo":
            albume_photos.append(InputMediaPhoto(
                media=file_id, caption=file_name))
            # await c.message.answer_photo(photo=file_id, caption=file_name)
        else:
            albume_docs.append(InputMediaDocument(
                media=file_id, caption=file_name))
            # await c.message.answer_document(document=file_id, caption=file_name)
    if albume_photos:
        await c.bot.send_media_group(c.message.chat.id, media=albume_photos)
    if albume_docs:
        await c.bot.send_media_group(c.message.chat.id, media=albume_docs)

    await dialog_manager.switch_to(TaskStates.DETAIL, show_mode=ShowMode.SEND)
    # await dialog_manager.show(show_mode=ShowMode.SEND)

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


async def on_toggle_completed_tasks(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Toggle showing completed tasks"""
    current = dialog_manager.dialog_data.get("show_completed", False)
    dialog_manager.dialog_data["show_completed"] = not current

    if not current:
        await callback.answer("✅ Показаны выполненные задачи")
    else:
        await callback.answer("✅ Выполненные задачи скрыты")


async def on_submit_task_button(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Handle 'Complete Task' button click - switch to result input state"""
    from bot.modules.states import OperatorTaskStates

    await dialog_manager.switch_to(OperatorTaskStates.SUBMIT_RESULT)


async def on_task_result_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Handle student's task result input"""
    from bot.modules.tasks.service import submit_task_result
    from bot.modules.states import StudentStates

    logger.debug(f"Dialog data: {dialog_manager.dialog_data}")
    logger.debug(f"Start data: {dialog_manager.start_data}")

    task_id = dialog_manager.start_data.get("task_id")

    if not task_id:
        await message.answer("❌ Ошибка: задача не найдена")
        await dialog_manager.switch_to(StudentStates.MY_TASKS)
        return

    # Submit task via API
    success = await submit_task_result(task_id, text)

    if success:
        await message.answer(
            "✅ Задача отправлена на проверку!\n"
            "Преподаватель получит уведомление и проверит вашу работу."
        )
        # Return to task list
        await dialog_manager.back()
    else:
        await message.answer("❌ Ошибка при отправке задачи. Попробуйте позже.")
        await dialog_manager.switch_to(StudentStates.MY_TASKS)


async def get_submitted_tasks_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for submitted tasks list (for operator)"""
    from bot.modules.tasks.service import get_submitted_tasks

    tasks = await get_submitted_tasks()

    # Add status emoji and index to each task
    for idx, task in enumerate(tasks):
        task["status_emoji"] = "📝"
        task["index"] = str(idx)

    # Store tasks in dialog_data for later retrieval by index
    dialog_manager.dialog_data["submitted_tasks"] = tasks

    return {
        "tasks": tasks,
        "tasks_count": len(tasks),
    }


async def on_submitted_task_select(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    """Handle submitted task selection for review"""
    # Get task by index from stored tasks
    tasks = dialog_manager.dialog_data.get("submitted_tasks", [])
    try:
        task_index = int(item_id)
        if 0 <= task_index < len(tasks):
            task_id = tasks[task_index]["id"]
            dialog_manager.dialog_data["selected_task_id"] = task_id
            from bot.modules.states import OperatorReviewStates
            await dialog_manager.switch_to(OperatorReviewStates.REVIEW_TASK_DETAIL)
        else:
            await callback.answer("❌ Задача не найдена")
    except (ValueError, IndexError, KeyError):
        await callback.answer("❌ Ошибка при выборе задачи")


async def get_review_task_detail_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Getter for task review detail view"""
    task_id = dialog_manager.dialog_data.get("selected_task_id")

    if not task_id:
        return {
            "task": {
                "title": "Ошибка",
                "description": "Задача не найдена",
                "result": "—",
                "start_date": "—",
                "due_date": "—",
            },
            "student_name": "—",
        }

    task = await tasks_service.get_task_by_id(task_id)

    if not task:
        return {
            "task": {
                "title": "Ошибка",
                "description": "Задача не найдена",
                "result": "—",
                "start_date": "—",
                "due_date": "—",
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

    task["start_date"] = start_date
    task["due_date"] = due_date
    task["result"] = task.get("result", "Не указан")

    # Get student info
    student_id = task.get("student_id")
    student_name = "Неизвестно"

    if student_id:
        # Get student name
        student = await user_service.get_user(student_id)
        if student:
            student_name = f"{student.get('first_name', '')} {student.get('last_name', '')}"

    return {
        "task": task,
        "student_name": student_name,
    }


async def on_approve_task(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Approve task completion"""
    from bot.modules.tasks.service import approve_task

    task_id = dialog_manager.dialog_data.get("selected_task_id")

    if not task_id:
        await callback.answer("❌ Ошибка: задача не найдена")
        return

    success = await approve_task(task_id)

    if success:
        await callback.answer("✅ Задача одобрена!")
        # TODO: Send notification to student
        from bot.modules.states import OperatorReviewStates
        await dialog_manager.switch_to(OperatorReviewStates.SUBMITTED_TASKS)
    else:
        await callback.answer("❌ Ошибка при одобрении задачи")


async def on_reject_task_button(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Handle 'Reject Task' button click - switch to comment input state"""
    from bot.modules.states import OperatorReviewStates

    # Switch to rejection comment input window
    await dialog_manager.switch_to(OperatorReviewStates.REJECT_TASK_COMMENT)


async def on_rejection_comment_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Handle operator's rejection comment input"""
    from bot.modules.tasks.service import reject_task
    from bot.modules.states import OperatorReviewStates

    task_id = dialog_manager.dialog_data.get("selected_task_id")

    if not task_id:
        await message.answer("❌ Ошибка: задача не найдена")
        await dialog_manager.switch_to(OperatorReviewStates.SUBMITTED_TASKS)
        return

    # Reject task via API
    success = await reject_task(task_id, text)

    if success:
        await message.answer(
            "✅ Задача отклонена!\n"
            "Студент получит уведомление с комментарием.\n"
            "Дедлайн продлен на 1 час."
        )
        # TODO: Send notification to student with rejection comment
        # Return to submitted tasks list
        await dialog_manager.switch_to(OperatorReviewStates.SUBMITTED_TASKS)
    else:
        await message.answer("❌ Ошибка при отклонении задачи")
        await dialog_manager.switch_to(OperatorReviewStates.SUBMITTED_TASKS)
