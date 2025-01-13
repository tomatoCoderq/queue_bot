import sqlite3
import os
import datetime

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from aiogram.filters import StateFilter, Command
from utilits import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter

router = Router()

conn = sqlite3.connect("database/db.db")
cursor = conn.cursor()


class SendPiece(StatesGroup):
    waiting_urgency = State()
    waiting_file = State()
    waiting_comments = State()


class IsStudent(BaseFilter):
    async def __call__(self, message: types.Message):
        role = [x[0] for x in cursor.execute(f"SELECT role FROM users WHERE idt={message.from_user.id}").fetchall()][0]
        # print(message.from_user.id, ids)
        return role == "student"




async def download_file(message: types.Message, bot: Bot) -> None:
    # Check whether path exists. Otherwise, create new
    if not os.path.exists(f"students_files/{message.from_user.id}"):
        os.makedirs(f"students_files/{message.from_user.id}")
        logger.info(f"Created new dir {message.from_user.id} in students_files")

    try:
        message_id = [x[0] for x in cursor.execute("SELECT id FROM requests_queue "
                                                   "WHERE proceeed=0 or proceeed=1").fetchall()][-1]
    except IndexError as e:
        logger.error("Error with message_id in download_file!")

    file_name = f"students_files/{message.from_user.id}/{message_id}?{datetime.date.today()}!{message.document.file_name}"
    open(file_name, "w").close()

    await bot.download(message.document, file_name)
    logger.info("Successfully downloaded document")


@router.message(Command("cancel"), IsStudent())
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Всё отменили, рабочих отослали.\nВыбирай, <b>Ученик!</b>", reply_markup=keyboards.keyboard_main_student(),
                                     parse_mode=ParseMode.HTML)

    await state.clear()


@router.callback_query(StateFilter(None), F.data == "send_piece")
async def send_piece(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("Выбери <b>приоритет</b> задачи: ",
                                     reply_markup=keyboards.keyboard_urgency_student(),
                                     parse_mode=ParseMode.HTML)
    await state.set_state(SendPiece.waiting_urgency)
    logger.info(f"{callback.message.from_user.username} sets state SendPiece.waiting_urgency")


@router.callback_query(F.data.in_({"high", "medium", "low"}), SendPiece.waiting_urgency)
async def get_urgency(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == "high":
        await state.update_data(urgency=1)
    if callback.data == "medium":
        await state.update_data(urgency=2)
    if callback.data == "low":
        await state.update_data(urgency=3)
    logger.info(f"Updated data. Urgency is {callback.data}")

    await state.set_state(SendPiece.waiting_comments)
    logger.info(f"{callback.message.from_user.username} sets state SendPiece.waiting_comments")

    await callback.message.edit_text("Пришлите текст", parse_mode=ParseMode.HTML)


@router.message(SendPiece.waiting_comments, F.text)
async def get_comments(message: types.Message, state: FSMContext, bot: Bot) -> None:
    await state.set_state(SendPiece.waiting_file)
    logger.info(f"{message.from_user.username} sets state SendPiece.waiting_file")

    await state.update_data(text=message.text)
    logger.info(f"Updated data. Urgency is {message.text}")

    await message.reply("Пришли файл для печати/резки\n<b>Внимание!</b> "
                        "Обрабатываются файлы только с расширением .stl или .dfx", parse_mode=ParseMode.HTML)


@router.message(SendPiece.waiting_file, F.document)
async def get_file_and_insert(message: types.Message, state: FSMContext, bot: Bot) -> object:
    file_type = message.document.file_name[-3:]

    # Check whether type of file is correct
    if file_type.lower() != "stl" and file_type.lower() != "dfx":
        logger.error(f"Wrong file type {file_type}")
        await message.reply("Неверный тип", parse_mode=ParseMode.HTML)
        return get_urgency

    data = await state.get_data()

    # Generate array to add data to table requests_queue in db.db
    to_add = [message.from_user.id, data['urgency'], file_type, 0,
              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data['text']]

    # Insert data to a table
    cursor.execute("INSERT INTO requests_queue VALUES (NULL, ?, ?, ?, ?, ?, ?)", to_add)
    conn.commit()
    logger.success(f"Added request from {message.from_user.username} to requests_queue")

    request_id = [x[0] for x in cursor.execute(
        "SELECT id FROM requests_queue WHERE proceeed=0 OR proceeed=1 order by urgency").fetchall()][-1]

    await download_file(message, bot)
    await message.reply(f"<b>Запрос с ID {request_id} отправлен в очередь</b>! Когда преподаватель возьмет его "
                        "на печать/резку, тебе отправят сообщение :0",
                        reply_markup=keyboards.keyboard_main_student(), parse_mode=ParseMode.HTML)

    await state.clear()
    logger.info("SendPiece FSM was cleared")


@router.callback_query(SendPiece.waiting_urgency, F.data == "back_to_main_student")
async def back(callback: types.callback_query, state: FSMContext):
    await callback.message.edit_text("Выбирай, <b>Ученик!</b>", reply_markup=keyboards.keyboard_main_student(),
                                     parse_mode=ParseMode.HTML)
    await state.clear()


