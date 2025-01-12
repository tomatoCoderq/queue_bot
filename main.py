import os
import sqlite3
from turtledemo.penrose import start

from aiogram import Bot, Dispatcher
from loguru import logger
import asyncio

from app.handlers import start_login
from app.handlers import start_registration
from app.handlers import student
from app.handlers import teacher
from app.handlers import test_handlers
from dotenv import load_dotenv


logger.add("logs.log", format="{time}| {level} | {message}", rotation="10MB")


async def main():
    logger.info("Bot has started!")

    load_dotenv()
    bot = Bot(token=os.getenv("TOKEN"))

    dp = Dispatcher()

    conn = sqlite3.connect("database/db.db")
    cursor = conn.cursor()

    # Creating tables in db.db. May be removed
    cursor.execute("CREATE TABLE IF NOT EXISTS users(idt integer primary key, user, role)")
    cursor.execute("CREATE TABLE IF NOT EXISTS students(idt integer primary key, name, surname)")

    # Here put requests that were added
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS requests_queue(id integer primary key autoincrement, idt, "
        "urgency, type, proceeed, time, comments)")

    # Routers from all handlers
    dp.include_router(student.router)
    dp.include_router(teacher.router)
    dp.include_router(start_registration.router)
    dp.include_router(start_login.router)


    # Dispatchers from all handlers
    start_registration.register_start_signup_handler(dp)
    # start_login.register_start_logging_handler(dp)
    test_handlers.register_test_handler(dp)


    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
