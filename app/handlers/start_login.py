from aiogram.enums import ParseMode
from aiogram.filters import Command
from app.utilits import keyboards
from app.utilits.database import database
from aiogram import Bot, types, Router
from loguru import logger
from app.utilits.messages import LoginMessages
from app.utilits.filters import IsRegistered

router = Router()


@router.message(Command('start'), IsRegistered())
async def start_logging(message: types.Message, bot: Bot):
    ids = database.fetchall("SELECT idt FROM users")
    roles = database.fetchall("SELECT role FROM users")

    ids_roles_dict = {ids[i]: roles[i] for i in range(len(ids))}

    # Registration of student
    if message.from_user.id in ids:
        if ids_roles_dict[message.from_user.id] == "student":
            await bot.send_message(chat_id=message.from_user.id, text=LoginMessages.welcome_student,
                                   reply_markup=keyboards.keyboard_main_student(), parse_mode=ParseMode.HTML)
            logger.info(f"{message.from_user.username} signed in as student")

        if ids_roles_dict[message.from_user.id] == "teacher":
            await bot.send_message(chat_id=message.from_user.id, text=LoginMessages.welcome_teacher,
                                   reply_markup=keyboards.keyboard_main_teacher(), parse_mode=ParseMode.HTML)
            logger.info(f"{message.from_user.username} signed in as teacher")

        # if dict[message.from_user.id] == "parent":
        #     await bot.send_message(chat_id=message.from_user.id, text="С возвращением, <b>Родитель</b>",
        #                            reply_markup=keyboards.KeyboardM(), parse_mode=ParseMode.HTML)
        #     logger.info(f"Signed in {message.from_user.username} as PARENT")
