import os
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from src.config import settings
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
from bot.modules.start.handlers import router
from bot.modules.start.windows import create_dialogs


dp = Dispatcher()


# TODO: migrate from direct sql quaries to orm

async def main():
    print("Starting bot...")

    bot = Bot(token=settings.telegram.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Include router first
    dp.include_router(router)
    
    # Setup dialogs
    setup_dialogs(dp)
    
    # Create and include dialogs
    registration_dialog, profile_dialog = create_dialogs()
    dp.include_router(registration_dialog)
    dp.include_router(profile_dialog)

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