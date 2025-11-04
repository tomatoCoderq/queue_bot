import os
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from src.config import settings
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
from bot.modules.start.handlers import router as start_router
from bot.modules.start.windows import create_dialogs
from bot.modules.tasks.windows import create_task_dialogs
from bot.modules.tasks.handlers import router as tasks_router


dp = Dispatcher()


# TODO: migrate from direct sql quaries to orm

async def main():
    print("Starting bot...")

    bot = Bot(token=settings.telegram.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(start_router)
    dp.include_router(tasks_router)
    
    # Setup dialogs
    setup_dialogs(dp)
    
    # Create and include start dialogs
    registration_dialog, profile_dialog = create_dialogs()
    dp.include_router(registration_dialog)
    dp.include_router(profile_dialog)
    
    # Create and include task dialogs
    student_tasks_dialog, operator_tasks_dialog = create_task_dialogs()
    dp.include_router(student_tasks_dialog)
    dp.include_router(operator_tasks_dialog)

    # Routers from all handlers
    # dp.include_router(client_details.router)
    # dp.include_router(operator_details.teacher_router)
    # dp.include_router(start.router)
    # dp.include_router(back_routes.router)
    # dp.include_router(test_handlers.router)
    # dp.include_router(client_equipment.router)
    # dp.include_router(operator_equipment.router)
    # dp.include_router(operator_students_cards.router)

    # await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())