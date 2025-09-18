from asyncio import sleep
from aiogram.filters import Command

from aiogram import Bot, types, Dispatcher, Router
from loguru import logger

from sqlalchemy import delete as sqla_delete, select

from src.storages.sql.dependencies import database
from src.storages.sql.models import requests_queue_table, students_table, users_table
from src.modules.shared.filters import IsTeacher

router = Router()
dp = Dispatcher()


@router.message(Command("announce"), IsTeacher())
async def announce(message: types.Message, bot: Bot):
    with database.session() as session:
        students_ids = session.scalars(select(students_table.c.idt)).all()

    to_send = ("<b>Внимание</b>! Просьба всех, кто приходит на занятие\n"
               "Всем спасибо :)")

    for id in students_ids:
        await bot.send_message(id, to_send)


'''TODO: Вынести в отдельный файл с общими helper функциями'''


async def help(message: types.Message):
    await message.answer("/cancel для отмены состояний\n/start если ничего не работает\n"
                         "если совсем ничего не работает писать @tomatocoder")


@router.message(Command("update"), IsTeacher())
async def update(message: types.Message, bot: Bot):
    with database.session() as session:
        students_ids = session.scalars(select(users_table.c.idt)).all()

    to_send = "Апдейт! Если что-то не работает, напишите, пожалуйста, @tomatocoder :)\n"
    for message in message.text.split()[1:]:
        to_send += f"{message}\t"

    for id in students_ids:
        await bot.send_message(id, to_send)


@router.message(Command("delete_teacher"), IsTeacher())
async def delete(message: types.Message, bot: Bot):
    username = message.text.split()

    if len(username) != 1:
        user = username[1]

        database.execute(
            sqla_delete(users_table).where(users_table.c.user == user)
        )

        await message.answer(f"{user} удален!")

        logger.success(f"{message.from_user.username} deleted admin {user}")


@router.message(Command("delete_student"), IsTeacher())
async def delete(message: types.Message, bot: Bot):
    username = message.text.split()

    if len(username) != 1:
        user = username[1]
        print(user)
        record = database.fetch_one(
            select(users_table.c.idt).where(users_table.c.user == user)
        )
        if not record:
            await message.answer(f"Пользователь {user} не найден.")
            return

        idt = record["idt"] if isinstance(record, dict) else record

        database.execute(
            sqla_delete(users_table).where(users_table.c.user == user)
        )
        database.execute(
            sqla_delete(students_table).where(students_table.c.idt == idt)
        )
        database.execute(
            sqla_delete(requests_queue_table).where(
                requests_queue_table.c.idt == idt)
        )

        await message.answer(f"{user} удален!")

        logger.success(f"{message.from_user.username} deleted admin {user}")

@router.message(Command("remind"))
async def remind(msg: types.Message):
    await msg.answer("Напомню через 5 секунд...")
    await sleep(5)
    await msg.answer("⏰ Напоминаю!")


def register_test_handler(dp: Dispatcher):
    dp.message.register(help, Command("help"))
    # dp.message.register(delete, Command("deleteadmin"))
    # dp.message.register(help, Command("cancel"))
