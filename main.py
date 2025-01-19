import os
import sqlite3
from email.policy import default

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.base import BaseSession
from aiogram.enums import ParseMode
from loguru import logger
import asyncio

from app.handlers import start_login
from app.handlers import start_registration
from app.handlers import student
from app.handlers import teacher
from app.handlers import test_handlers
from app.handlers import student_queue
from dotenv import load_dotenv
from app.handlers import test_handlers

logger.add("logs.log", format="{time}| {level} | {message}", rotation="10MB")
dp = Dispatcher()


# TODO: migrate from direct sql quaries to orm

async def main():
    logger.info("Bot has started!")

    load_dotenv()
    bot = Bot(token=os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        conn = sqlite3.connect("database/db.db", timeout=7)
        cursor = conn.cursor()

        # Creating tables in db.db. May be removed
        cursor.execute("CREATE TABLE IF NOT EXISTS users(idt integer primary key, user, role)")
        cursor.execute("CREATE TABLE IF NOT EXISTS students(idt integer primary key, name, surname)")

        # Here put requests that were added
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS requests_queue(id integer primary key autoincrement, idt, "
            "urgency, type, proceeed, time, comments)")

    except sqlite3.OperationalError as e:
        logger.error("HUGE BD MISTAKE")

    # Routers from all handlers
    dp.include_router(student.router)
    dp.include_router(teacher.router)
    dp.include_router(start_registration.router)
    dp.include_router(start_login.router)
    dp.include_router(student_queue.router)
    dp.include_router(test_handlers.router)


    # Dispatchers from all handlers
    start_registration.register_start_signup_handler(dp)
    # start_login.register_start_logging_handler(dp)
    test_handlers.register_test_handler(dp)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
