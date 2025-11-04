from aiogram import Router, types
from aiogram.filters.command import CommandStart
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram.types import CallbackQuery, Message

from bot.modules.start.windows import RegistrationStates, ProfileStates
from bot.modules.start.service import get_user, create_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, dialog_manager: DialogManager):
    """Handle /start command - check if user is registered"""
    if not message.from_user:
        return
        
    telegram_id = message.from_user.id
    user = await get_user(telegram_id)
    
    if user:
        # User is registered, go to profile
        await dialog_manager.start(
            ProfileStates.PROFILE,
            mode=StartMode.RESET_STACK,
            data={"telegram_id": telegram_id}
        )
    else:
        # User is not registered, start registration from ROLE_CHOICE
        await dialog_manager.start(
            RegistrationStates.ROLE_CHOICE,
            mode=StartMode.RESET_STACK,
        )


async def on_role_select(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Handle role selection"""
    role_map = {
        "role_student": "student",
        "role_parent": "parent",
        "role_operator": "operator",
    }
    
    widget_id = button.widget_id or "role_student"
    role = role_map.get(widget_id, "student")
    dialog_manager.dialog_data["role"] = role
    
    await dialog_manager.switch_to(RegistrationStates.FIRST_NAME)


async def on_first_name_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle first name input"""
    dialog_manager.dialog_data["first_name"] = data
    await dialog_manager.switch_to(RegistrationStates.LAST_NAME)


async def on_last_name_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    """Handle last name input"""
    dialog_manager.dialog_data["last_name"] = data
    
    # Save username from telegram
    if message.from_user:
        username = message.from_user.username or "no_username"
        dialog_manager.dialog_data["username"] = username
    else:
        dialog_manager.dialog_data["username"] = "no_username"
    
    await dialog_manager.switch_to(RegistrationStates.CONFIRM)


async def on_confirm_registration(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Handle registration confirmation"""
    telegram_id = callback.from_user.id
    first_name = dialog_manager.dialog_data["first_name"]
    last_name = dialog_manager.dialog_data["last_name"]
    username = dialog_manager.dialog_data["username"]
    role = dialog_manager.dialog_data["role"]
    
    # Create user via API
    await create_user(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        role=role,
    )
    
    await dialog_manager.switch_to(RegistrationStates.SUCCESS)


async def on_cancel_registration(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Handle registration cancellation"""
    # Clear data and go back to role choice
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(RegistrationStates.ROLE_CHOICE)


async def on_success_complete(**kwargs):
    """Getter for SUCCESS state - transition happens via cmd_start"""
    return {}


async def get_profile_data(dialog_manager: DialogManager, **kwargs):
    """Getter for profile window - load user data"""
    telegram_id = None
    
    if isinstance(dialog_manager.start_data, dict):
        telegram_id = dialog_manager.start_data.get("telegram_id")
    
    if not telegram_id and dialog_manager.event.from_user:
        telegram_id = dialog_manager.event.from_user.id
    
    if not telegram_id:
        return {
            "first_name": "Unknown",
            "last_name": "User",
            "role": "unknown",
            "role_display": "Неизвестная",
            "username": "unknown",
            "tasks_button_text": "📚 Задачи",
        }
    
    user = await get_user(telegram_id)
    
    if user:
        role = user["role"].lower()
        
        # Map role to display text and button text
        role_display_map = {
            "student": "Студент",
            "operator": "Оператор",
            "parent": "Родитель",
        }
        
        tasks_button_map = {
            "student": "📚 Мои задачи",
            "operator": "👥 Студенты и задачи",
            "parent": "🚧 В разработке",
        }
        
        return {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "role": role,
            "role_display": role_display_map.get(role, role.capitalize()),
            "username": user["username"],
            "tasks_button_text": tasks_button_map.get(role, "📚 Задачи"),
        }
    
    return {
        "first_name": "Unknown",
        "last_name": "User",
        "role": "unknown",
        "role_display": "Неизвестная",
        "username": "unknown",
        "tasks_button_text": "📚 Задачи",
    }


async def on_menu_tasks(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Handle 'My Tasks' button click - different behavior based on role"""
    if not callback.from_user:
        return
    
    telegram_id = callback.from_user.id
    user = await get_user(telegram_id)
    
    if not user:
        await callback.answer("Ошибка: пользователь не найден")
        return
    
    role = user.get("role", "").lower()
    
    if role == "student":
        # Import here to avoid circular import
        from bot.modules.start.windows import StudentStates
        await dialog_manager.start(
            StudentStates.MY_TASKS,
            mode=StartMode.NORMAL,
        )
    elif role == "operator":
        # Import here to avoid circular import
        from bot.modules.start.windows import OperatorStates
        await dialog_manager.start(
            OperatorStates.STUDENTS_LIST,
            mode=StartMode.NORMAL,
        )
    elif role == "parent":
        await callback.answer("🚧 Функционал для родителей в разработке")
    else:
        await callback.answer("Неизвестная роль пользователя")



async def on_menu_settings(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Handle 'Settings' button click"""
    await callback.answer("Настройки в разработке...")


async def on_menu_logout(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Handle 'Logout' button click"""
    await callback.answer("До встречи!")
    await dialog_manager.done()

