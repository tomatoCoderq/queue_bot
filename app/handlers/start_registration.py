import sqlite3

from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utilits import keyboards

from aiogram import Bot, types, Dispatcher, Router
from loguru import logger
from aiogram.filters import BaseFilter
import os
from dotenv import load_dotenv

conn = sqlite3.connect("database/db.db")
cursor = conn.cursor()

router = Router()
dp = Dispatcher()


class RegistrationState(StatesGroup):
    waiting_data = State()


class IsNotRegistered(BaseFilter):
    async def __call__(self, message: types.Message):
        ids = [x[0] for x in cursor.execute("SELECT idt FROM users").fetchall()]
        print(message.from_user.id, ids)
        return message.from_user.id not in ids


@router.message(Command('start'), IsNotRegistered())
async def start_signup(message: types.Message, bot: Bot):
    logger.info(f"{message.from_user.username} started process of signing up")

    ids = [x[0] for x in cursor.execute("SELECT idt FROM users").fetchall()]

    # Registration of student
    if message.from_user.id not in ids:
        await message.answer(text="Привет! Это <b>DigitalQueue</b> бот для создания удобной цифровой очереди. "
                                  "\n<i>Выберите одну из доступных ролей:</i>",
                             parse_mode=ParseMode.HTML, reply_markup=keyboards.keyboard_start_registration())


@dp.callback_query(F.data == "teacher")
async def add_teacher(callback: types.CallbackQuery):
    logger.info(f"{callback.message.from_user.username} has chosen role teacher")

    to_add = [callback.from_user.id, callback.from_user.username, "teacher"]

    load_dotenv()
    teachers = [alias for alias in os.getenv("TEACHER_IDS", "").split(",")]

    if callback.from_user.username in teachers:
        # TODO: Write try catch
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", to_add)
        conn.commit()
        logger.success(f"Added {callback.from_user.username} to database Users as <b>teacher</b>")

        await callback.message.edit_text("<b>Выбрана роль Оператора!</b> Чтобы получить больше информации напишите /help",
                                         reply_markup=keyboards.keyboard_main_teacher(), parse_mode=ParseMode.HTML)
        await callback.answer("Успешная регистрация")

    else:
        logger.error(f"User {callback.from_user.username} tried to sign up as teacher")
        await callback.answer("Вы не можете выбрать роль Оператора! Выберите другую роль")
        # await callback.message.edit_text("Ты не преподаватель! Выбери другую роль",
        #                                  reply_markup=keyboards.keyboard_start_registration(),
        #                                  parse_mode=ParseMode.HTML)



@router.callback_query(F.data == "student")
async def requesting_data_student(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напишите Имя и Фамилию:\n"
                                     "<i>Например: Иван Иванов</i>", parse_mode=ParseMode.HTML)
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

        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", to_add_users)
        logger.success(f"Added {message.from_user.username} to database Users as student")

        cursor.execute("INSERT INTO students VALUES (?, ?, ?)", to_add_students)
        logger.success(f"Added {message.from_user.username} to database Students as {name} {surname}")

        conn.commit()

        await message.reply("<b>Выбрана роль Клиента!</b> Чтобы получить больше информации напишите /help ",
                            reply_markup=keyboards.keyboard_main_student(), parse_mode=ParseMode.HTML)

    await state.clear()


def register_start_signup_handler(dp: Dispatcher):
    dp.callback_query.register(add_teacher, F.data == "teacher")
