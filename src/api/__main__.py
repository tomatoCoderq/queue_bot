"""Application entry point for the queue bot."""
from __future__ import annotations

import asyncio
import os
from typing import Iterable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs
from dotenv import load_dotenv
from loguru import logger

from src.modules.shared import back_routes
from src.modules.tasks.handlers import add_tasks, proceed as teacher_proceed_tasks
from src.modules.client.handlers import details as client_details, equipment as client_equipment
from src.modules.operator.handlers import (
    details as operator_details,
    equipment as operator_equipment,
    students_cards as operator_students_cards,
    tasks_queue as teacher_tasks_queue,
)
from src.modules.auth.handlers import start
from src.modules.auth.dialog import auth_dialog
from src.modules.tasks.dialog import tasks_dialog
from src.modules.operator.dialog import operator_tasks_dialog
from src.modules.admin.handlers import test_handlers
from src.storages.sql.dependencies import database

async def main() -> None:
    """Configure and run the AIogram application."""
    logger.add("logs.log", format="{time}| {level} | {message}", rotation="10MB")
    logger.info("Bot initialising")

    load_dotenv()
    token = os.getenv("TOKEN")
    if not token:
        raise RuntimeError("TOKEN is not set in environment variables")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher()

    # Setup aiogram_dialog
    dispatcher.include_router(auth_dialog)
    dispatcher.include_router(tasks_dialog)
    dispatcher.include_router(operator_tasks_dialog)
    setup_dialogs(dispatcher)

    # _ensure_schema()

    dispatcher.include_router(client_details.router)
    dispatcher.include_router(operator_details.teacher_router)
    dispatcher.include_router(start.router)
    dispatcher.include_router(back_routes.router)
    dispatcher.include_router(test_handlers.router)
    dispatcher.include_router(client_equipment.router)
    dispatcher.include_router(operator_equipment.router)
    dispatcher.include_router(operator_students_cards.router)
    dispatcher.include_router(add_tasks.router)
    dispatcher.include_router(teacher_proceed_tasks.router)
    dispatcher.include_router(teacher_tasks_queue.router)

    test_handlers.register_test_handler(dispatcher)

    asyncio.create_task(add_tasks.scheduler(bot))

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
