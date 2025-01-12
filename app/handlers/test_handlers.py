import sqlite3
from aiogram.filters import Command

from aiogram import Bot, types, Dispatcher, Router
from loguru import logger
import os

# from start_registration import teachers

conn = sqlite3.connect("database/db.db")
cursor = conn.cursor()
logger.info("connected to db.db in start.py")

router = Router()
dp = Dispatcher()


# delete all data from tables and role
# def add_teacher(teacher_id):
#
#     with open(".env", "r") as file:
#         lines = file.readlines()
#
#     # Initialize a variable to hold updated .env content
#     updated_lines = []
#     teacher_ids_set = set()
#
#     for line in lines:
#         if line.startswith("TEACHER_IDS"):
#             # Extract current teacher IDs from the line
#             current_teacher_ids = line.strip().split("=")[1]
#             teacher_ids_set = set(current_teacher_ids.split(",")) if current_teacher_ids else set()
#
#             # Add the new teacher ID (ensuring uniqueness)
#             teacher_ids_set.add(str(teacher_id))
#
#             # Reconstruct the TEACHER_IDS line
#             updated_line = f"TEACHER_IDS={','.join(teacher_ids_set)}\n"
#             updated_lines.append(updated_line)
#         else:
#             updated_lines.append(line)
#
#     # If the TEACHER_IDS variable was not found, add it
#     if not any(line.startswith("TEACHER_IDS") for line in lines):
#         teacher_ids_set.add(str(teacher_id))
#         updated_lines.append(f"TEACHER_IDS={','.join(teacher_ids_set)}\n")
#
#     # Write the updated content back to the .env file
#     with open(".env", "w") as file:
#         file.writelines(updated_lines)
#
#
# #add_admins
# async def add(message: types.Message):
#     if len(message.text.split()) < 2:
#         await message.answer("Команда и Имя")
#         return add
#
#     # print(message.text.split()[1])
#     add_teacher(message.text.split()[1])
#     await message.answer("сдеалаон")
#
#

async def help(message: types.Message):
    await message.answer("Тут будет хелп")


async def delete(message: types.Message):
    # cursor.execute(f"DELETE FROM users WHERE idt={message.from_user.id}")
    # cursor.execute(f"DELETE FROM students")
    # cursor.execute(f"DELETE FROM parents")
    # conn.commit()
    # logger.success(f"Deleted {message.from_user.username} from database")
    sent_message = await message.answer("Welcome! Use /next to continue.")

    await message.delete()


def register_test_handler(dp: Dispatcher):
    dp.message.register(help, Command("help"))
