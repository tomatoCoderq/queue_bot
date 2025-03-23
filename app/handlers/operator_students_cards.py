from app.handlers.teacher_tasks_queue import map_names_and_idt
from app.utils.files import *
from app.models.operator import Operator
from app.managers.operator_manager import OperatorManagerDetails, OperatorManagerStudentCards
from app.fsm_states.operator_states import CheckMessage, ReturnToQueue, ShowClientCard
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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

    # @router.callback_query(F.data == "clients")
# async def show_all_clients_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
#     teacher = Operator(callback.from_user.id, callback.from_user.username)
#     manager = OperatorManagerStudentCards(teacher)
#     await manager.all_users_penalties_show(callback, state)
#

# @router.message(ShowClientCard.get_client_id, F.text)
# async def show_client_card_handler(message: types.Message, state: FSMContext, bot: Bot):
#     teacher = Operator(message.from_user.id, message.from_user.username)
#     manager = OperatorManagerStudentCards(teacher)
#     await manager.show_client_card(message, state)


@router.callback_query(ShowClientCard.get_client_id)
async def show_client_card_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    idt = callback.data.split("_")[-1]  # extract student ID
    await state.update_data(idt=idt)

    teacher = Operator(callback.from_user.id, callback.from_user.username)
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
    teacher = Operator(message.from_user.id, message.from_user.username)
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


# @router.callback_query(F.data == "removetask")
# async def remove_all_tasks_handler(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
#     teacher = Operator(callback.from_user.id, callback.from_user.username)
#     manager = OperatorManagerDetails(teacher)
#     await manager.show_details_queue(callback)


@router.callback_query(F.data == "setpenalty", ShowClientCard.further_actions)
async def ask_penalty_reason_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите причину штрафа:")
    await callback.message.delete()
    await state.set_state(ShowClientCard.get_penalty_reasons)


@router.message(F.text, ShowClientCard.get_penalty_reasons)
async def add_penalty_handler(message: types.Message, state: FSMContext):
    teacher = Operator(message.from_user.id, message.from_user.username)
    manager = OperatorManagerStudentCards(teacher)
    await manager.add_penalty(message, state, reason=message.text)
    await state.clear()


@router.callback_query(F.data == "removepenalty", ShowClientCard.further_actions)
async def ask_penalty_id_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ID штрафа для удаления:")
    await callback.message.delete()
    await state.set_state(ShowClientCard.get_penalty_id_to_delete)


@router.message(F.text, ShowClientCard.get_penalty_id_to_delete)
async def remove_penalty_handler(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Введите числовой ID штрафа.")
        return

    teacher = Operator(message.from_user.id, message.from_user.username)
    manager = OperatorManagerStudentCards(teacher)
    await manager.remove_penalty(message, int(message.text))
    await state.clear()


@router.callback_query(F.data == "bk", ShowClientCard.further_actions)
async def back_to_main_teacher_handler(callback: types.CallbackQuery, state: FSMContext):
    teacher = Operator(callback.from_user.id, callback.from_user.username)
    manager = OperatorManagerStudentCards(teacher)
    await manager.back_to_main_teacher(callback, state)

# `@router.message(CheckMessage.waiting_size, F.text)
# async def finish_work_get_params_handler(message: types.Message, state: FSMContext):
#     teacher = Operator(message.from_user.id, message.from_user.username)
#     manager = OperatorManagerDetails(teacher)
#     await manager.finish_work_get_params(message, state)
# `
