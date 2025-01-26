import os
import datetime

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command

from app.utilits import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter

from app.utilits.database import database
from app.utilits.keyboards import CallbackDataKeys
# from main import dp
from app.handlers.teacher import create_idt_name_map
from app.utilits.filters import IsStudent
from app.utilits.messages import StudentMessages

router = Router()
dp = Dispatcher()


class SendPiece(StatesGroup):
    waiting_urgency = State()
    waiting_file = State()
    waiting_comments = State()
    waiting_amount = State()


async def download_file(message: types.Message, bot: Bot) -> None:
    # Check whether path exists. Otherwise, create new
    if not os.path.exists(f"students_files/{message.from_user.id}"):
        os.makedirs(f"students_files/{message.from_user.id}")
        logger.info(f"Created new dir {message.from_user.id} in students_files")

    try:
        message_id = database.fetchall("SELECT id FROM requests_queue "
                                       "WHERE proceeed=0 or proceeed=1")[-1]
        # message_id = [x[0] for x in cursor.execute("SELECT id FROM requests_queue "
        #                                            "WHERE proceeed=0 or proceeed=1").fetchall()][-1]
    except IndexError as e:
        logger.error("Error with message_id in download_file!")

    file_name = f"students_files/{message.from_user.id}/{message_id}?{datetime.date.today()}!{message.document.file_name}"
    open(file_name, "w").close()

    await bot.download(message.document, file_name)
    logger.success("Successfully downloaded document")


@router.message(Command("cancel"), IsStudent())
async def cancel(message: types.Message, state: FSMContext):
    await message.answer(
        StudentMessages.cancel_process,
        reply_markup=keyboards.keyboard_main_student(),
        parse_mode=ParseMode.HTML,
    )
    await state.clear()


@router.callback_query(StateFilter(None), F.data == "send_piece")
async def send_piece(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        StudentMessages.urgency_selection,
        reply_markup=keyboards.keyboard_urgency_student(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(SendPiece.waiting_urgency)
    logger.info(f"{callback.message.from_user.username} sets state SendPiece.waiting_urgency")


@router.callback_query(F.data.in_({"high", "medium", "low"}), SendPiece.waiting_urgency)
async def get_urgency(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if callback.data == "high":
        await state.update_data(urgency=2)
        await state.update_data(to_approve_urgency=True)
    elif callback.data == "medium":
        await state.update_data(urgency=2)
    elif callback.data == "low":
        await state.update_data(urgency=3)

    logger.info(f"Updated data. Urgency is {callback.data}")
    await state.set_state(SendPiece.waiting_amount)

    logger.info(f"{callback.message.from_user.username} sets state SendPiece.waiting_comments")

    await callback.message.edit_text(StudentMessages.priority_chosen, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.in_({"high", "medium", "low"}))
async def get_urgency_while_canceled(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer(StudentMessages.invalid_priority_cancelled)


@router.message(SendPiece.waiting_amount, F.text)
async def get_amount(message: types.Message, state: FSMContext, bot: Bot) -> object:
    if not message.text.isdigit():
        await message.answer(StudentMessages.INVALID_AMOUNT_INPUT)
        return get_amount

    await message.answer(StudentMessages.AMOUNT_ACCEPTED)
    await state.set_state(SendPiece.waiting_comments)
    await state.update_data(amount=message.text)


@router.message(SendPiece.waiting_comments, F.text)
async def get_comments(message: types.Message, state: FSMContext, bot: Bot) -> None:
    await state.set_state(SendPiece.waiting_file)
    logger.info(f"{message.from_user.username} sets state SendPiece.waiting_file")

    await state.update_data(text=message.text)
    logger.info(f"Updated data. Urgency is {message.text}")

    await message.reply(StudentMessages.description_accepted, parse_mode=ParseMode.HTML)


@router.message(SendPiece.waiting_file, F.document)
async def get_file_and_insert(message: types.Message, state: FSMContext, bot: Bot) -> object:
    file_type = message.document.file_name[-3:]

    if file_type.lower() not in {"stl", "dxf"}:
        logger.error(f"Wrong file type {file_type}")
        await message.reply(StudentMessages.invalid_file_extension, parse_mode=ParseMode.HTML)
        return

    data = await state.get_data()

    to_add = [
        message.from_user.id,
        data["urgency"],
        file_type,
        0,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data["text"],
        data['amount'],
        message.document.file_name[:-4],
        0,
        0
    ]

    database.execute("INSERT INTO requests_queue VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", to_add)
    logger.success(f"Added request from {message.from_user.username} to requests_queue")

    # Get last added ID to send to user
    request_id = database.fetchall("SELECT id FROM requests_queue")[-1]


    await download_file(message, bot)

    await message.reply(
        StudentMessages.request_queued.format(request_id=request_id), parse_mode=ParseMode.HTML
    )
    await message.answer(
        StudentMessages.choose_next_action,
        reply_markup=keyboards.keyboard_main_student(),
        parse_mode=ParseMode.HTML,
    )

    if "to_approve_urgency" in data.keys():
        names = create_idt_name_map()
        # idt = database.fetchall("SELECT idt FROM users WHERE proceeed=1 or proceeed=0")
        for teacher in database.fetchall("SELECT idt FROM users WHERE role='teacher'"):
            await bot.send_message(
                teacher, f"запрос {request_id} от {names[message.from_user.id][0]} {names[message.from_user.id][1]}", reply_markup=keyboards.keyboard_process_high_urgency_teacher()
            )
    await state.clear()
    logger.info("SendPiece FSM was cleared")


@router.callback_query(F.data.in_({CallbackDataKeys.confirm_high_urgency, CallbackDataKeys.reject_high_urgency}))
async def process_high_urgency(callback: types.CallbackQuery) -> None:
    if callback.data == CallbackDataKeys.confirm_high_urgency:
        id_to_change = callback.message.text.split()[1]

        database.execute("UPDATE requests_queue SET urgency=? WHERE id=?", (1, id_to_change))
        logger.success("UPDATED urgency=3 after confirm by Operator")

        await callback.answer(StudentMessages.HIGH_URGENCY_ACCEPTED)
        await callback.message.delete()

    else:
        await callback.answer(StudentMessages.HIGH_URGENCY_REJECTED)
        await callback.message.delete()


@router.callback_query(SendPiece.waiting_urgency, F.data == "back_to_main_student")
async def back(callback: types.callback_query, state: FSMContext):
    await callback.message.edit_text(
        StudentMessages.choose_next_action,
        reply_markup=keyboards.keyboard_main_student(),
        parse_mode=ParseMode.HTML,
    )
    await state.clear()
