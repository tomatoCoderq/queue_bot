import os
import sys

from aiogram import Bot, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from src.fsm_states.operator_states import CheckMessage, ReturnToQueue, ShowClientCard
from src.modules.operator.handlers.tasks_queue import map_names_and_idt
from src.modules.models.operator import Operator
from src.modules.operator.manager import OperatorManagerDetails, OperatorManagerStudentCards

router = Router()


def get_student_selection_keyboard():
    students = map_names_and_idt()  # {idt: (surname, name)}

    buttons = []
    for idt, (surname, name) in students.items():
        # alias = generate_student_alias(surname, name, idt)
        btn = InlineKeyboardButton(
            text=f"{surname} {name}",
            callback_data=f"student_alias_{idt}"
        )
        buttons.append([btn])  # one button per row

    buttons.append([InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_main_teacher")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "clients")
async def show_all_clients_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.edit_text(
        "<b>Выберите ученика:</b>",
        reply_markup=get_student_selection_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()
    await state.set_state(ShowClientCard.get_client_id)

    # @router.callback_query(F.data == "clients"


@router.callback_query(ShowClientCard.get_client_id)
async def show_client_card_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    idt = callback.data.split("_")[-1]  # extract student ID
    await state.update_data(idt=idt)

    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerStudentCards(teacher)
    await manager.show_client_card(callback, state)


@router.callback_query(F.data.in_({"t1", "t2"}), ShowClientCard.further_actions)
async def ask_task_change_handler(callback: types.CallbackQuery, state: FSMContext):
    task_number = 1 if callback.data == "t1" else 2
    await callback.message.answer(f"Введите новое описание для задачи {task_number}:")
    await state.update_data(task_number=task_number)
    await state.set_state(ShowClientCard.get_changed_task)
    await callback.message.delete()


@router.message(F.text, ShowClientCard.get_changed_task)
async def handle_task_change_handler(message: types.Message, state: FSMContext, bot: Bot):
    teacher = Operator(message.from_user.id)
    manager = OperatorManagerStudentCards(teacher)
    data = await state.get_data()
    await manager.change_task(message, state, task_number=data["task_number"])


@router.callback_query(F.data == "settask", ShowClientCard.further_actions)
async def ask_first_task(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите первую задачу:")
    await callback.message.delete()
    await state.set_state(ShowClientCard.set_tasks_one)


@router.message(F.text, ShowClientCard.set_tasks_one)
async def ask_second_task(message: types.Message, state: FSMContext):
    await message.answer("Введите вторую задачу:")
    await state.update_data(task_one=message.text)
    await state.set_state(ShowClientCard.set_tasks_two)


@router.message(F.text, ShowClientCard.set_tasks_two)
async def finalize_task_set(message: types.Message, state: FSMContext):
    teacher = Operator(message.from_user.id, message.from_user.username)
    manager = OperatorManagerStudentCards(teacher)
    data = await state.get_data()

    await manager.set_all_tasks(message, state, data["task_one"], message.text)
    # await message.answer("✅ Обе задачи добавлены", reply_markup=keyboards.keyboard_main_teacher())
    await state.clear()


@router.callback_query(F.data == "setpenalty", ShowClientCard.further_actions)
async def ask_penalty_reason_handler(callback: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🧹 Неубранное рабочее место", callback_data="penalty_messy_desk")],
        [types.InlineKeyboardButton(text="👟 Отсутствие второй обуви", callback_data="penalty_no_shoes")],
    ])
    await callback.message.edit_text("Выберите причину штрафа:", reply_markup=keyboard)

    await state.set_state(ShowClientCard.get_penalty_reasons)
    await callback.answer()


@router.callback_query(F.data.in_(["penalty_messy_desk", "penalty_no_shoes"]), ShowClientCard.get_penalty_reasons)
async def ask_whether_send_photo(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(reason=callback.data)

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Да", callback_data="penalty_send_photo_yes")],
        [types.InlineKeyboardButton(text="Нет", callback_data="penalty_send_photo_no")]]
    )
    await callback.message.edit_text("Хотите прислать фотографию?", reply_markup=keyboard)
    await state.set_state(ShowClientCard.get_whether_wants_photo)
    await callback.answer()


@router.callback_query(F.data == "penalty_send_photo_no", ShowClientCard.get_whether_wants_photo)
async def add_penalty_without_photo(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    reason = data["reason"]

    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerStudentCards(teacher)
    await manager.add_penalty(callback, state, reason)


@router.callback_query(F.data == "penalty_send_photo_yes", ShowClientCard.get_whether_wants_photo)
async def prompt_for_penalty_photo(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Пришлите, пожалуйста, фотографию штрафа.")
    await state.set_state(ShowClientCard.waiting_penalty_photo)
    await callback.answer()


@router.message(ShowClientCard.waiting_penalty_photo, F.photo)
async def receive_penalty_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    client_id = data["idt"]
    reason = data["reason"]
    photo = message.photo[-1].file_id

    teacher = Operator(message.from_user.id)
    manager = OperatorManagerStudentCards(teacher)
    await manager.add_penalty_with_photo(message, state, reason, photo)


@router.callback_query(F.data == "removepenalty", ShowClientCard.further_actions)
async def ask_penalty_id_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ID штрафа для удаления:")
    # await callback.message.delete()
    await state.set_state(ShowClientCard.get_penalty_id_to_delete)
    await state.update_data(msg_id=callback.message.message_id)


@router.message(F.text, ShowClientCard.get_penalty_id_to_delete)
async def remove_penalty_handler(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Введите числовой ID штрафа.")
        return

    teacher = Operator(message.from_user.id)
    manager = OperatorManagerStudentCards(teacher)
    await manager.remove_penalty(message, int(message.text), state)
    # await state.clear()


@router.message(Command("restart"))
async def restart_bot(message: types.Message, bot: Bot):
    load_dotenv()
    teacher_ids = os.getenv("TEACHER_IDS").split(",")

    print(teacher_ids)
    if message.from_user.username not in teacher_ids:
        return await message.reply("Нет прав для перезапуска бота.")

    await message.reply("Перезапускаюсь…")

    # # вариант A: полностью заменить текущий процесс новым
    os.execv(sys.executable, [sys.executable, "main.py"])

# @router.callback_query(F.data == "bk", ShowClientCard.further_actions)
# async def back_to_main_teacher_handler(callback: types.CallbackQuery, state: FSMContext):
#     teacher = Operator(callback.from_user.id)
#     manager = OperatorManagerStudentCards(teacher)
#     await manager.back_to_main_teacher(callback, state)

# `@router.message(CheckMessage.waiting_size, F.text)
# async def finish_work_get_params_handler(message: types.Message, state: FSMContext):
#     teacher = Operator(message.from_user.id, message.from_user.username)
#     manager = OperatorManagerDetails(teacher)
#     await manager.finish_work_get_params(message, state)
# `
