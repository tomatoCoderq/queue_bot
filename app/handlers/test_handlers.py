from aiogram.filters import Command

from aiogram import Bot, types, Dispatcher, Router
from loguru import logger

from app.utilits.database import database
from app.utilits.filters import IsTeacher
# from start_registration import teachers

# conn = sqlite3.connect("database/db.db")
# cursor = conn.cursor()
# logger.info("connected to db.db in start.py")

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



@router.message(Command("update"), IsTeacher())
async def update(message:types.Message, bot: Bot):
    students_ids = database.fetchall("SELECT idt FROM users")

    to_send = "Апдейт! Если что-то не работает, напишите, пожалуйста, @tomatocoder :)\n"
    for message in message.text.split()[1:]:
        to_send += f"{message}\t"

    for id in students_ids:
        await bot.send_message(id, to_send)


async def help(message: types.Message):
    await message.answer("/cancel для отмены состояний\n/start если ничего не работает\n"
                         "если совсем ничего не работает писать @tomatocoder")


@router.message(Command("delete_teacher"), IsTeacher())
async def delete(message: types.Message, bot: Bot):
    username = message.text.split()

    if len(username) != 1:
        user = username[1]

        database.execute(f"DELETE FROM users WHERE user=?", (user, ))

        await message.answer(f"{user} удален!")

        logger.success(f"{message.from_user.username} deleted admin {user}")


@router.message(Command("delete_student"), IsTeacher())
async def delete(message: types.Message, bot: Bot):
    username = message.text.split()

    if len(username) != 1:
        user = username[1]
        print(user)
        idt = database.fetchall(f"SELECT idt from users where user=?", (user, ))
        print(idt)

        database.execute(f"DELETE FROM users WHERE user=?", (user, ))
        database.execute(f"DELETE FROM students WHERE idt=?", (idt[0],))
        database.execute(f"DELETE FROM requests_queue WHERE idt=?", (idt[0],))

        await message.answer(f"{user} удален!")

        logger.success(f"{message.from_user.username} deleted admin {user}")


def register_test_handler(dp: Dispatcher):
    dp.message.register(help, Command("help"))
    # dp.message.register(delete, Command("deleteadmin"))
    # dp.message.register(help, Command("cancel"))
