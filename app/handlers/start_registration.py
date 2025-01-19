from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.utilits import keyboards

from aiogram import Bot, types, Dispatcher, Router
from loguru import logger
from aiogram.filters import BaseFilter
import os
from dotenv import load_dotenv
from app.utilits.keyboards import CallbackDataKeys
from app.utilits.database import database
from app.utilits.filters import IsNotRegistered
from app.utilits.messages import RegistrationMessages

router = Router()
dp = Dispatcher()


class RegistrationState(StatesGroup):
    waiting_data = State()


@router.message(Command('start'), IsNotRegistered())
async def start_signup(message: types.Message, bot: Bot):
    logger.info(f"{message.from_user.username} started process of signing up")

    ids = database.fetchall("SELECT idt FROM users")

    if message.from_user.id not in ids:
        await message.answer(
            text=RegistrationMessages.welcome_message,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.keyboard_start_registration(),
        )


@dp.callback_query(F.data == CallbackDataKeys.start_registration_operator)
async def add_teacher(callback: types.CallbackQuery):
    logger.info(f"{callback.message.from_user.username} has chosen role teacher")

    to_add = [callback.from_user.id, callback.from_user.username, "teacher"]

    load_dotenv()
    teachers = [alias for alias in os.getenv("TEACHER_IDS", "").split(",")]

    if callback.from_user.username in teachers:
        database.execute("INSERT INTO users VALUES (?, ?, ?)", to_add)
        logger.success(f"Added {callback.from_user.username} to database Users as <b>teacher</b>")

        await callback.message.edit_text(
            RegistrationMessages.teacher_role_chosen,
            reply_markup=keyboards.keyboard_main_teacher(),
            parse_mode=ParseMode.HTML,
        )
        await callback.answer("Успешная регистрация")

    else:
        logger.error(f"User {callback.from_user.username} tried to sign up as teacher")
        await callback.answer(RegistrationMessages.teacher_registration_failed)


@router.callback_query(F.data == CallbackDataKeys.start_registration_client)
async def requesting_data_student(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        RegistrationMessages.student_provide_name, parse_mode=ParseMode.HTML
    )
    await callback.answer()

    await state.update_data(waiting_data="student")
    await state.set_state(RegistrationState.waiting_data)


@router.message(RegistrationState.waiting_data, F.text)
async def add_students_parents(message: types.Message, state: FSMContext):
    data = await state.get_data()

    to_add_users = [message.from_user.id, message.from_user.username, data['waiting_data']]
    name, surname = message.text.split()[0], message.text.split()[1]

    if data['waiting_data'] == "student":
        to_add_students = [message.from_user.id, name, surname]

        database.execute("INSERT INTO users VALUES (?, ?, ?)", to_add_users)
        logger.success(f"Added {message.from_user.username} to database Users as student")

        database.execute("INSERT INTO students VALUES (?, ?, ?)", to_add_students)
        logger.success(f"Added {message.from_user.username} to database Students as {name} {surname}")

        await message.reply(
            RegistrationMessages.student_role_chosen,
            reply_markup=keyboards.keyboard_main_student(),
            parse_mode=ParseMode.HTML,
        )

    await state.clear()


def register_start_signup_handler(dp: Dispatcher):
    dp.callback_query.register(add_teacher, F.data == CallbackDataKeys.start_registration_operator)
