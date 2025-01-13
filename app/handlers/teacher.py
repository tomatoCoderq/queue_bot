import sqlite3
from datetime import datetime
from pyexpat.errors import messages

import aiogram.exceptions
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from aiogram.filters import Command

from utilits import keyboards

from aiogram import Bot, types, Router
from loguru import logger
from typing import Dict
import os

router = Router()
conn = sqlite3.connect("database/db.db")
cursor = conn.cursor()


class MessageState(StatesGroup):
    waiting_message = State()
    waiting_approve_reject = State()


class CheckMessage(StatesGroup):
    waiting_id = State()
    waiting_action = State()
    waiting_photo_report = State()


def create_idt_name_map() -> map:
    cursor.execute("""
    SELECT requests_queue.idt, students.name, students.surname FROM requests_queue INNER JOIN students 
    ON requests_queue.idt = students.idt
    """)

    idt_name_map = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

    return idt_name_map


def urgency_int_to_str(urgency: int) -> str:
    if urgency == 1:
        return "Высокая"
    if urgency == 2:
        return "Средняя"
    if urgency == 3:
        return "Низкая"


def status_int_to_str(status: int) -> str:
    if status == 0:
        return "Не в работе"
    if status == 1:
        return "В работе"


def generate_message_to_send(students_messages) -> str:
    cidt_name_map = create_idt_name_map()

    message_to_send = [
        (f"<b>ID</b>: {students_messages[i][0]}\n<b>Имя</b>: {cidt_name_map[students_messages[i][1]][0]} "
         f"{cidt_name_map[students_messages[i][1]][1]}\n"
         f"<b>Тип</b>: {students_messages[i][3]}\n"
         f"<b>Срочность</b>: {urgency_int_to_str(students_messages[i][2])}\n"
         f"<b>Статус</b>: {status_int_to_str(students_messages[i][4])}\n---\n") for i in range(len(students_messages))]

    s = ''
    if len(message_to_send) == 0:
        s += "Очередь пуста и запросов нет!"
    else:
        for a in message_to_send:
            s += a
    return s


@router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Всё отменили, рабочих отослали.\nВыбирай, <b>Преподаватель!</b>", reply_markup=keyboards.keyboard_main_teacher(),
                                     parse_mode=ParseMode.HTML)

    await state.clear()


@router.callback_query(F.data.in_({"sort_urgency", "sort_date", "sort_type"}))
async def sort(callback: types.CallbackQuery, state: FSMContext) -> None:
    students_messages = []
    if callback.data == "sort_urgency":
        students_messages = [x for x in cursor.execute(
            "SELECT * FROM requests_queue WHERE proceeed=0 OR proceeed=1 order by urgency").fetchall()]
    if callback.data == "sort_date":
        students_messages = [x for x in cursor.execute(
            "SELECT * FROM requests_queue WHERE proceeed=0 OR proceeed=1 ORDER BY time").fetchall()]
    if callback.data == "sort_type":
        students_messages = [x for x in cursor.execute(
            "SELECT * FROM requests_queue WHERE proceeed=0 OR proceeed=1 ORDER BY type").fetchall()]

    s = generate_message_to_send(students_messages)
    try:
        await callback.message.edit_text(s, reply_markup=keyboards.keyboard_sort_teacher(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest as e:
        # TODO: Change this handling
        None

    await state.set_state(CheckMessage.waiting_id)
    logger.info(f"{callback.message.from_user.username} sets state CheckMessage.waiting_id")

    await callback.answer()


@router.callback_query(F.data.in_({"back_to_queue", "check"}))
async def check_messages(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    students_messages = [x for x in
                         cursor.execute("SELECT * FROM requests_queue WHERE proceeed=0 OR proceeed=1").fetchall()]

    s = generate_message_to_send(students_messages)
    data = await state.get_data()

    if callback.data == "check":
        msg = await callback.message.edit_text(s, reply_markup=keyboards.keyboard_sort_teacher(),
                                               parse_mode=ParseMode.HTML)
    else:
        try:
            # await bot.delete_message(callback.message.from_user.id, data['msg'])
            await callback.message.delete()
        except aiogram.exceptions.TelegramBadRequest as e:
            logger.error(f"Occurred {e} with id {data['msg']}")
        msg = await callback.message.answer(s, reply_markup=keyboards.keyboard_sort_teacher(),
                                            parse_mode=ParseMode.HTML)
    await state.set_state(CheckMessage.waiting_id)
    logger.info(f"{callback.message.from_user.username} sets state CheckMessage.waiting_id")

    await state.update_data(msg=msg.message_id)
    print(msg.message_id)
    logger.info(f"{callback.message.from_user.username} updates state data msg={msg.message_id}")

    await callback.answer()


@router.message(CheckMessage.waiting_id, F.text)
async def waiting_id(message: types.Message, state: FSMContext, bot: Bot) -> object:
    # Fix taking all data and putting info whether it was taken or not
    messages_ids = [x[0] for x in
                    cursor.execute("SELECT id FROM requests_queue WHERE proceeed=0 or proceeed=1").fetchall()]
    messages_students = [x for x in
                         cursor.execute("SELECT * FROM requests_queue WHERE proceeed=0 or proceeed=1").fetchall()]
    students_ids = [x[0] for x in
                    cursor.execute("SELECT idt FROM requests_queue WHERE proceeed=0 or proceeed=1").fetchall()]

    if not message.text.isdigit() or int(message.text) not in messages_ids:
        await message.reply("Такого ID <b>нет</b> в списке!. Попробуйте еще раз", parse_mode=ParseMode.HTML)
        logger.error(f"Wrong id was written by {message.from_user.username}")
        return check_messages

    spdict = {messages_ids[i]: students_ids[i] for i in range(len(messages_ids))}

    data = await state.get_data()

    # Delete previous message and message sent by user
    try:
        await bot.delete_message(message.from_user.id, data['msg'])
        await message.delete()
    except aiogram.exceptions.TelegramBadRequest as e:
        logger.error(f"Occurred {e}")
    logger.info(f"Deleting message from user and previous message with id {data['msg']}")

    message_to_send = ''

    cidt_name_map = create_idt_name_map()

    for i in range(len(messages_students)):
        if messages_students[i][0] == int(message.text):
            message_to_send = (f"<b>ID</b>: {messages_students[i][0]}\n"
                               f"<b>Имя</b>: {cidt_name_map[messages_students[i][1]][0]} "
                               f"{cidt_name_map[messages_students[i][1]][1]}\n"
                               f"<b>Срочность</b>: {urgency_int_to_str(messages_students[i][2])}\n"
                               f"<b>Тип</b>: {messages_students[i][3]}\n"
                               f"<b>Время</b>: {messages_students[i][5]}\n"
                               f"<b>Комментарий</b>: {messages_students[i][6]}\n")
            await state.update_data(id=messages_students[i][0], idt=messages_students[i][1])
            break

    # Find file name with specific ID given by user
    file_name = [entry for entry in os.listdir(f'students_files/{spdict[int(message.text)]}') if
                 entry.startswith(message.text)]

    msg = await message.answer_document(
        document=types.FSInputFile(f"students_files/{spdict[int(message.text)]}/{file_name[0]}"),
        caption=message_to_send, reply_markup=keyboards.keyboard_teacher_actions(), parse_mode=ParseMode.HTML)

    await state.set_state(CheckMessage.waiting_action)
    logger.info(f"{message.from_user.username} sets state CheckMessage.waiting_action")

    await state.update_data(msg=msg.message_id)
    logger.info(f"{message.from_user.username} updates state data msg={msg.message_id}")


@router.callback_query(CheckMessage.waiting_action, F.data == "accept")
async def take_on_work(callback: types.CallbackQuery, bot: Bot, state: FSMContext) -> object:
    data = await state.get_data()

    messages_ids = [x[0] for x in cursor.execute("SELECT id FROM requests_queue WHERE proceeed=0").fetchall()]

    if data['id'] in messages_ids:
        cursor.execute(f"UPDATE requests_queue SET proceeed=1 WHERE id={data['id']}")
        conn.commit()

        logger.success("File was take on work")
        await bot.send_message(data['idt'], f"Ваша деталь с ID {data['id']} принята на печать/резку")
        await callback.answer("Принято на работу", reply_markup=keyboards.keyboard_main_teacher())
    else:
        logger.error("File was already taken on work")
        await callback.answer("Уже в работе", reply_markup=keyboards.keyboard_main_teacher())
        return waiting_id

    # logger.info("CheckMessage FSM was cleared")


@router.callback_query(CheckMessage.waiting_action, F.data == "end")
async def finish_work(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    is_proceed = [x[0] for x in
                    cursor.execute(f"SELECT proceeed FROM requests_queue WHERE id={data['id']}").fetchall()][0]
    if is_proceed == 0:
        await callback.answer("Работа еще не была принята на работу!")
    if is_proceed == 1:
        await callback.message.delete()
        msg = await callback.message.answer("Пришлите фотографию отчет печати/резки", parse_mode=ParseMode.HTML)

        await state.set_state(CheckMessage.waiting_photo_report)
        await callback.answer()
        await state.update_data(msg=msg.message_id)
        logger.info(f"{callback.message.from_user.username} sets state CheckMessage.waiting_photo_report")


def delete_file(data) -> None:
    messages_ids = [x[0] for x in
                    cursor.execute("SELECT id FROM requests_queue WHERE proceeed=0 or proceeed=1").fetchall()]

    students_ids = [x[0] for x in
                    cursor.execute("SELECT idt FROM requests_queue WHERE proceeed=0 or proceeed=1").fetchall()]

    spdict = {messages_ids[i]: students_ids[i] for i in range(len(messages_ids))}

    document_name = [entry for entry in os.listdir(f'students_files/{spdict[int(data["id"])]}') if
                     entry.startswith(str(data['id']))]

    try:
        os.remove(f"students_files/{spdict[data['id']]}/{document_name[0]}")
    except OSError as e:
        logger.error(f"Occurred {e}")


@router.message(CheckMessage.waiting_photo_report, F.photo)
async def finish_work_report(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()

    print(data['msg'])
    # await message.delete()
    await bot.delete_message(message.from_user.id, int(data['msg']))

    delete_file(data)

    cursor.execute(f"UPDATE requests_queue SET proceeed=2 WHERE id={data['id']}")
    conn.commit()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_name = f"temporal/{data['idt']}{current_time}.jpg"
    open(file_name, "w").close()

    await bot.download(message.photo[-1], f"temporal/{data['idt']}{current_time}.jpg")
    await bot.send_photo(data['idt'], photo=types.FSInputFile(f"temporal/{data['idt']}{current_time}.jpg"),
                         caption=f"Ваша работа с ID {data['id']} завершена!")

    try:
        os.remove(f"temporal/{data['idt']}{current_time}.jpg")
    except OSError as e:
        logger.error(f"Occurred {e}")

    await message.answer("Деталь была отправлена <b>ученику</b>.\nЗапрос больше <b>не будет</b> отображаться в очереди",
                         parse_mode=ParseMode.HTML, reply_markup=keyboards.keyboard_main_teacher())

    await state.clear()
    logger.success("CheckMessage FSM was cleared")


@router.callback_query(CheckMessage.waiting_id, F.data == "back_to_main_teacher")
async def back_to_main_teacher(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.edit_text("Выбирайте, Преподаватель", reply_markup=keyboards.keyboard_main_teacher())

    data = await state.get_data()
    print(data)
    # try:
    #     await bot.delete_message(callback.message.from_user.id, int(data['msg']))
    # except aiogram.exceptions.TelegramBadRequest as e:
    #     logger.error(f"Occurred {e} with id {data['msg']}")
    await callback.answer()
    await state.clear()
