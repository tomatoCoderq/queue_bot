import asyncio.subprocess
import os
import sqlite3
import time
from email.policy import default

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.base import BaseSession
from aiogram.enums import ParseMode
from loguru import logger
from asyncio import *
import aioschedule as schedule


from app.handlers import start_login
from app.handlers import start_registration
from app.handlers import student
from app.handlers import teacher
from app.handlers import test_handlers
from app.handlers import student_queue
from dotenv import load_dotenv
from app.handlers import test_handlers
from app.handlers import teacher_history
from app.handlers import teacher_get_xlsx
from app.handlers import add_tasks
from app.handlers import teacher_proceed_tasks
from app.handlers import teacher_tasks_queue
from app.handlers import penalty

from xlsxwriter.workbook import Workbook

logger.add("logs.log", format="{time}| {level} | {message}", rotation="10MB")
dp = Dispatcher()


# TODO: migrate from direct sql quaries to orm

async def main():
    logger.info("Bot has started!")

    load_dotenv()
    bot = Bot(token=os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        # ToDO: rewrite this to database class
        conn = sqlite3.connect("database/db.db", timeout=7)
        cursor = conn.cursor()

        # Creating tables in db.db. May be removed
        cursor.execute("CREATE TABLE IF NOT EXISTS users(idt integer primary key, user, role)")
        cursor.execute("CREATE TABLE IF NOT EXISTS students(idt integer primary key, name, surname)")

        # Here put requests that were added
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS requests_queue(id integer primary key autoincrement, idt, "
            "urgency, type, proceeed, time, comments)")

        cursor.execute("CREATE TABLE IF NOT EXISTS tasks(id integer primary key, idt, task_first, "
                       "task_second, start_time, status, shift)")

        cursor.execute("CREATE TABLE IF NOT EXISTS penalty(id integer primary key, idt, reason)")

    except (sqlite3.OperationalError, sqlite3.Error) as e:
        logger.error(f"HUGE BD MISTAKE: {e}")

    # os.environ['TZ'] = 'Europe/Moscow'
    # time.tzset()
    # time.strftime('%X %x')

    # Routers from all handlers
    dp.include_router(student.router)
    dp.include_router(teacher.teacher_router)
    dp.include_router(start_registration.router)
    dp.include_router(start_login.router)
    dp.include_router(student_queue.router)
    dp.include_router(test_handlers.router)
    dp.include_router(teacher_history.router)
    dp.include_router(teacher_get_xlsx.router)
    dp.include_router(add_tasks.router)
    dp.include_router(teacher_proceed_tasks.router)
    dp.include_router(teacher_tasks_queue.router)
    dp.include_router(penalty.router)


    # Dispatchers from all handlers
    start_registration.register_start_signup_handler(dp)
    # start_login.register_start_logging_handler(dp)
    test_handlers.register_test_handler(dp)

    asyncio.create_task(add_tasks.scheduler(bot))

    await dp.start_polling(bot)
#
# async def on_startup():
#     asyncio.create_task(add_tasks.job())

if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(add_tasks.job())
    # asyncio.run(on_startup())
