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


from app.handlers import start
from app.handlers import client_details
from app.handlers import operator_details
from app.handlers import test_handlers
from app.handlers import student_queue
from dotenv import load_dotenv
from app.handlers import test_handlers
from app.handlers import add_tasks
from app.handlers import teacher_proceed_tasks
from app.handlers import teacher_tasks_queue
from app.handlers import penalty
from app.handlers import details
from app.handlers import details_client

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

        # All details one by one
        cursor.execute("CREATE TABLE IF NOT EXISTS details(id integer primary key, name, price, owner)")

        cursor.execute("""CREATE TABLE IF NOT EXISTS detail_aliases (name, alias)""")

    except (sqlite3.OperationalError, sqlite3.Error) as e:
        logger.error(f"HUGE BD MISTAKE: {e}")

    # os.environ['TZ'] = 'Europe/Moscow'
    # time.tzset()
    # time.strftime('%X %x')

    # Routers from all handlers
    dp.include_router(client_details.router)
    dp.include_router(operator_details.teacher_router)
    dp.include_router(start.router)
    dp.include_router(student_queue.router)
    dp.include_router(test_handlers.router)
    dp.include_router(add_tasks.router)
    dp.include_router(teacher_proceed_tasks.router)
    dp.include_router(teacher_tasks_queue.router)
    dp.include_router(penalty.router)
    dp.include_router(details.router)
    dp.include_router(details_client.router)


    # Dispatchers from all handlers
    # start_login.register_start_logging_handler(dp)
    test_handlers.register_test_handler(dp)

    asyncio.create_task(add_tasks.scheduler(bot))

    # await bot.delete_webhook()
    await dp.start_polling(bot)
#
# async def on_startup():
#     asyncio.create_task(add_tasks.job())

if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(add_tasks.job())
    # asyncio.run(on_startup())
