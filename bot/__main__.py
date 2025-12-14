from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from bot.logs import setup_bot_logger
from src.config import settings
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio

from bot.modules.start.handlers import router as start_router
from bot.modules.tasks.handlers import router as tasks_router
from bot.modules.groups.handlers import router as groups_router
from bot.modules.users.handlers import router as users_router

from bot.modules.start.windows import create_dialogs
from bot.modules.tasks.windows import create_task_dialogs
from bot.modules.groups.windows import create_group_dialogs
from bot.modules.users.windows import create_user_dialogs
# from bot.modules.groups.windows import create_group_dialogs
from loguru import logger

from bot.scheduler import setup_scheduler, shutdown_scheduler


dp = Dispatcher()

async def main():
    setup_bot_logger()
        
    logger.info("Starting bot...")

    bot = Bot(token=settings.telegram.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(start_router)
    dp.include_router(users_router)
    dp.include_router(groups_router)
    dp.include_router(tasks_router)
    
    # Setup dialogs
    setup_dialogs(dp)
    
    # Create and include start dialogs
    registration_dialog, profile_dialog = create_dialogs()
    dp.include_router(registration_dialog)
    dp.include_router(profile_dialog)

    client_dialog, update_user_dialog = create_user_dialogs()
    dp.include_router(client_dialog)
    dp.include_router(update_user_dialog)
    
    # Create and include group dialogs
    groups_dialog, create_group_dialog, client_groups_dialog = create_group_dialogs()
    dp.include_router(groups_dialog)
    dp.include_router(create_group_dialog)
    dp.include_router(client_groups_dialog)
    
    # Create and include task dialogs
    operator_task_create_dialog, operator_review_dialog, tasks_dialog = create_task_dialogs()
    dp.include_router(operator_task_create_dialog)
    dp.include_router(operator_review_dialog)
    dp.include_router(tasks_dialog)
    
    
    # Setup scheduler
    await setup_scheduler()

    try:
        await dp.start_polling(bot)
    finally:
        # Shutdown scheduler on bot shutdown
        await shutdown_scheduler()

if __name__ == "__main__":
    asyncio.run(main())