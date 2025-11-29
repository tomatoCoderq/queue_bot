from aiogram import Router, types
from aiogram.filters.command import CommandStart
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram.types import CallbackQuery, Message

from bot.modules.states import ClientGroupsStates, OperatorTaskStates, RegistrationStates, ProfileStates

from bot.modules.users import service as user_service
from bot.modules.groups import service as group_service
from src import config

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, dialog_manager: DialogManager):
    '''Проверяем что юзер зарегистрирован и запускаем нужный диалог'''
    if not message.from_user:
        return

    telegram_id = message.from_user.id
    alias = message.from_user.username
    user = await user_service.get_user(telegram_id)

    if user:
        # User is registered
        await dialog_manager.start(
            ProfileStates.PROFILE,
            mode=StartMode.RESET_STACK,
            data={"telegram_id": telegram_id,
                  "alias": alias}
        )
    else:
        # User is not registered, start registration from ROLE_CHOICE
        await dialog_manager.start(
            RegistrationStates.ROLE_CHOICE,
            mode=StartMode.RESET_STACK,
            data={"telegram_id": telegram_id,
                  "alias": alias}
        )


async def on_role_select(c, b, dialog_manager: DialogManager,):
    """Handle role selection"""
    role_map = {
        "role_student": "student",
        "role_parent": "parent",
        "role_operator": "operator",
    }

    widget_id = b.widget_id or "role_student"
    role = role_map.get(widget_id, "student")
    
    admins = config.settings.telegram.ADMIN_IDS.split(",")
    if role == "operator" and dialog_manager.start_data.get("alias") not in admins:
        await c.answer("❌ У вас нет прав оператора.")
        return
    
    if role == "parent":
        await c.answer("❌ Роль 'Родитель' пока недоступна.")
        return
    
    dialog_manager.dialog_data["role"] = role

    await dialog_manager.switch_to(RegistrationStates.FIRST_NAME)


async def on_first_name_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_manager.dialog_data["first_name"] = data
    await dialog_manager.switch_to(RegistrationStates.LAST_NAME)


async def on_last_name_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_manager.dialog_data["last_name"] = data

    # Save username from telegram
    username = message.from_user.username or "no_username"
    dialog_manager.dialog_data["username"] = username

    await dialog_manager.switch_to(RegistrationStates.CONFIRM)


async def on_confirm_registration(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Confirm registration"""
    telegram_id = callback.from_user.id
    first_name = dialog_manager.dialog_data["first_name"]
    last_name = dialog_manager.dialog_data["last_name"]
    username = dialog_manager.dialog_data["username"]
    role = dialog_manager.dialog_data["role"]

    # Create user via API
    await  user_service.create_user(
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
    dialog_manager.dialog_data.clear()  # Clear all gathered data
    await dialog_manager.switch_to(RegistrationStates.ROLE_CHOICE)


async def get_profile_data(dialog_manager: DialogManager, **kwargs):
    """Getter for profile window"""
    telegram_id = None

    telegram_id = dialog_manager.start_data.get("telegram_id")

    if not telegram_id and dialog_manager.event.from_user:
        telegram_id = dialog_manager.event.from_user.id

    if not telegram_id:
        raise ValueError("Telegram ID not found for profile data retrieval")

    user = await user_service.get_user(telegram_id)

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
            "is_operator": role == "operator",
        }

    raise ValueError("User not found")


async def on_menu_tasks(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """First button behavior based on role"""
    if not callback.from_user:
        return

    telegram_id = callback.from_user.id
    user = await user_service.get_user(telegram_id)

    if not user:
        await callback.answer("Ошибка: пользователь не найден")
        return

    role = user.get("role", "").lower()

    if role == "":
        await callback.answer("Ошибка: роль пользователя не определена")
        return

    if role == "student":
        await dialog_manager.start(
            OperatorTaskStates.LIST_TASKS,
            mode=StartMode.NORMAL,
            data={
                "context":"student_self",
                "telegram_id": telegram_id
            }
        )
    elif role == "operator":
        from bot.modules.states import OperatorStudentsStates

        await dialog_manager.start(
            OperatorStudentsStates.STUDENTS_LIST,
            mode=StartMode.NORMAL,
        )

    elif role == "parent":
        await callback.answer("🚧 Функционал для родителей в разработке")


async def on_groups_tasks(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager,):
    """Group management depedens on role"""
    from bot.modules.states import OperatorGroupsStates

    if not callback.from_user:
        return

    telegram_id = callback.from_user.id
    user = await user_service.get_user(telegram_id)

    if not user:
        await callback.answer("Ошибка: пользователь не найден")
        return

    role = user.get("role", "").lower()

    if role == "student":
        group_id = await group_service.get_client_group(telegram_id)
        if group_id is None:
            await callback.answer("Вы не в группе")
        else:    
            await dialog_manager.start(
                ClientGroupsStates.GROUP_INFO,
                mode=StartMode.NORMAL,
                data={"telegram_id": telegram_id}
            )

    if role == "operator":
        await dialog_manager.start(
            OperatorGroupsStates.GROUP_LIST,
            mode=StartMode.NORMAL,
        )


async def on_menu_settings(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Settings button. In progress"""
    await callback.answer("Настройки в разработке...")


async def on_menu_review_tasks(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Review tasks button for operators"""
    from bot.modules.states import OperatorReviewStates
    from aiogram_dialog import StartMode

    await dialog_manager.start(
        OperatorReviewStates.SUBMITTED_TASKS,
        mode=StartMode.NORMAL,
    )
