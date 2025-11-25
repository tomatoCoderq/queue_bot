import asyncio.subprocess
import os
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger
from asyncio import *


from app.handlers import start
from app.handlers import client_details
from app.handlers import operator_details
from app.handlers import test_handlers
from dotenv import load_dotenv
from app.handlers import add_tasks
from app.utils import back_routes
# from app.handlers import details_client
from app.handlers import operator_students_cards
from app.handlers import client_equipment
from app.handlers import operator_equipment


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

    # Routers from all handlers
    dp.include_router(client_details.router)
    dp.include_router(operator_details.teacher_router)
    dp.include_router(start.router)
    dp.include_router(back_routes.router)
    dp.include_router(test_handlers.router)
    dp.include_router(client_equipment.router)
    dp.include_router(operator_equipment.router)
    dp.include_router(operator_students_cards.router)


    # Dispatchers from all handlers
    test_handlers.register_test_handler(dp)

    asyncio.create_task(add_tasks.scheduler(bot))

    # await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())