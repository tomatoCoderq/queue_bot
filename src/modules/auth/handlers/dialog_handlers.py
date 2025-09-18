"""Handlers for auth module using aiogram_dialog."""

import os
from typing import Any

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message, User, CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import insert, select

from src.modules.auth.states import AuthSG
from src.modules.shared.filters import IsNotRegistered, IsRegistered
from src.modules.shared.messages import LoginMessages, RegistrationMessages
from src.storages.sql.dependencies import database
from src.storages.sql.models import UserModel, students_table, users_table

router = Router()


# ==================== COMMAND HANDLERS ====================

@router.message(Command("start"), IsRegistered())
async def start_registered(
    message: Message, dialog_manager: DialogManager, **kwargs
) -> None:
    """Handle /start command for registered users."""
    # Check user role and redirect to appropriate menu
    user = database.fetch_one(
        select(users_table).where(users_table.c.idt == message.from_user.id),
        model=UserModel,
    )
    
    if user:
        await dialog_manager.start(state=AuthSG.choose_role, mode=StartMode.RESET_STACK)
        if user.role == "student":
            await dialog_manager.switch_to(AuthSG.main_menu_student)
            logger.info(f"{message.from_user.username} signed in as student")
        elif user.role == "teacher":
            await dialog_manager.switch_to(AuthSG.main_menu_teacher)
            logger.info(f"{message.from_user.username} signed in as teacher")


@router.message(Command("start"), IsNotRegistered())
async def start_unregistered(
    message: Message, dialog_manager: DialogManager, **kwargs
) -> None:
    """Handle /start command for unregistered users."""
    logger.info(f"{message.from_user.username} started registration process")
    
    # Check if user is already in database
    user_ids = {
        user.idt
        for user in database.fetch_all(select(users_table), model=UserModel)
    }
    
    if message.from_user.id not in user_ids:
        await dialog_manager.start(state=AuthSG.choose_role, mode=StartMode.RESET_STACK)


@router.message(Command("myid"))
async def get_my_id(message: Message) -> None:
    """Get user's Telegram ID."""
    await message.answer(
        f"Ваш Telegram ID: <code>{message.from_user.id}</code>",
        parse_mode="HTML"
    )


# ==================== REGISTRATION HANDLERS ====================

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
