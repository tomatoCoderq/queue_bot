"""Registration handlers for auth module."""

import os
from typing import Any

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import insert, select

from src.modules.auth.states import AuthSG
from src.modules.shared.messages import RegistrationMessages
from src.storages.sql.dependencies import database
from src.storages.sql.models import UserModel, students_table, users_table


async def process_student_registration(
    message: Message,
    widget,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Process student registration."""
    try:
        name_parts = text.strip().split()
        if len(name_parts) != 2:
            await message.answer("❌ Пожалуйста, введите имя и фамилию через пробел.")
            return
            
        name, surname = name_parts
        
        # Register user
        database.execute(
            insert(users_table).values(
                idt=message.from_user.id,
                user=message.from_user.username,
                role="student",
            )
        )
        logger.success(f"Added {message.from_user.username} to database Users as student")
        
        # Register student details
        database.execute(
            insert(students_table).values(
                idt=message.from_user.id,
                name=name,
                surname=surname,
            )
        )
        logger.success(f"Added {message.from_user.username} to database Students as {name} {surname}")
        
        await message.answer(
            RegistrationMessages.student_role_chosen,
            parse_mode="HTML"
        )
        
        # Switch to student menu
        await dialog_manager.switch_to(AuthSG.main_menu_student)
        
    except Exception as e:
        logger.error(f"Error registering student: {e}")
        await message.answer("❌ Ошибка при регистрации. Попробуйте позже.")


async def process_teacher_registration(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
) -> None:
    """Process teacher registration."""
    load_dotenv()
    teachers = [alias for alias in os.getenv("TEACHER_IDS", "").split(",")]
    
    logger.debug(f"TEACHER_IDS from .env: {teachers}")
    
    if callback.from_user.username in teachers:
        try:
            database.execute(
                insert(users_table).values(
                    idt=callback.from_user.id,
                    user=callback.from_user.username,
                    role="teacher",
                )
            )
            logger.success(f"Added {callback.from_user.username} to database Users as teacher")
            
            await callback.message.answer(
                RegistrationMessages.teacher_role_chosen,
                parse_mode="HTML"
            )
            
            # Switch to teacher menu
            await dialog_manager.switch_to(AuthSG.main_menu_teacher)
            
        except Exception as e:
            logger.error(f"Error registering teacher: {e}")
            await callback.message.answer("❌ Ошибка при регистрации. Попробуйте позже.")
    else:
        logger.error(f"User {callback.from_user.username} tried to sign up as teacher")
        await callback.message.answer(RegistrationMessages.teacher_registration_failed)
        await dialog_manager.switch_to(AuthSG.choose_role)


async def on_student_role_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager
):
    """Handler for student role selection."""
    dialog_manager.dialog_data["selected_role"] = "student"
    await dialog_manager.switch_to(AuthSG.student_name_input)


async def on_teacher_role_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager
):
    """Handler for teacher role selection."""
    dialog_manager.dialog_data["selected_role"] = "teacher"
    await dialog_manager.switch_to(AuthSG.teacher_confirm)


async def on_cancel_teacher(
    callback: CallbackQuery, widget, dialog_manager: DialogManager
):
    """Handler for teacher role cancellation."""
    await dialog_manager.switch_to(AuthSG.choose_role)


async def on_menu_action(
    callback: CallbackQuery, widget, dialog_manager: DialogManager
):
    """Placeholder handler for menu actions."""
    await callback.answer("Функция в разработке")
