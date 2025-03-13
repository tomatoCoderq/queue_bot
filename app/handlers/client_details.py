import os
import datetime

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command

from app.models.operator import Operator

from aiogram import Bot, types, Router

from app.managers.client_manager import ClientManager
from app.models.client import Client
from app.fsm_states.client_states import SendPiece

router = Router()
dp = Dispatcher()

# TODO: Write a class Student to handle all operations with it


@router.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext):
    # Create a Student instance; real applications might fetch additional info.
    idt_name_map = Operator.get_idt_name_map()
    student = Client(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )
    manager = ClientManager(student)
    await manager.cancel_upload(message, state)


@router.callback_query(F.data == "send_piece")
async def send_piece_handler(callback: types.CallbackQuery, state: FSMContext):
    idt_name_map = Operator.get_idt_name_map()
    student = Client(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username
    )
    print(student.full_card())
    manager = ClientManager(student)
    await manager.initiate_send_piece(callback, state)


@router.callback_query(F.data.in_( {"high", "medium", "low"}), SendPiece.waiting_urgency)
async def urgency_handler(callback: types.CallbackQuery, state: FSMContext):
    idt_name_map = Operator.get_idt_name_map()
    student = Client(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username
    )
    manager = ClientManager(student)
    await manager.process_urgency(callback, state)


@router.message(SendPiece.waiting_amount, F.text)
async def amount_handler(message: types.Message, state: FSMContext):
    idt_name_map = Operator.get_idt_name_map()
    student = Client(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )
    manager = ClientManager(student)
    await manager.process_amount(message, state)


@router.message(SendPiece.waiting_comments, F.text)
async def comments_handler(message: types.Message, state: FSMContext):
    idt_name_map = Operator.get_idt_name_map()
    student = Client(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )
    manager = ClientManager(student)
    await manager.process_comments(message, state)


@router.message(SendPiece.waiting_file, F.document)
async def file_upload_handler(message: types.Message, state: FSMContext, bot: Bot):
    idt_name_map = Operator.get_idt_name_map()
    student = Client(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )
    manager = ClientManager(student)
    await manager.process_file_upload(message, state, bot)


@router.callback_query(F.data == "back_to_main_student")
async def back_to_main_handler(callback: types.CallbackQuery, state: FSMContext):
    idt_name_map = Operator.get_idt_name_map()
    student = Client(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username
    )
    manager = ClientManager(student)
    await manager.back_to_main_student(callback, state)


@router.callback_query(F.data.in_( {"confirm_high_urgency", "reject_high_urgency"} ))
async def high_urgency_handler(callback: types.CallbackQuery):
    idt_name_map = Operator.get_idt_name_map()
    student = Client(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username
    )
    manager = ClientManager(student)
    await manager.process_high_urgency_decision(callback)