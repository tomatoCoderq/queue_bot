from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher

from app.utilits import keyboards
from aiogram import Bot, types, Router

from app.utilits.database import database
from app.utilits.keyboards import CallbackDataKeys
from app.handlers.teacher_tasks_queue import map_names_and_idt
from app.utilits.messages import TeacherMessages

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


class UserTask:
    def __init__(self, idt, task_first, task_second):
        self.idt = idt
        self.task_first = task_first
        self.task_second = task_second


router = Router()
dp = Dispatcher()


class ShowClientPenaltyCard(StatesGroup):
    get_client_id = State()
    further_actions = State()
    get_penalty_reasons = State()
    get_penalty_id_to_delete = State()


def form_the_message_with_penalties():
    message_to_send = TeacherMessages.ENTER_USER_ID
    names_ids = map_names_and_idt()

    for idt, name in names_ids.items():
        number_of_penalties = database.fetchall("Select count(id) from penalty where idt=?", (str(idt),))
        message_to_send += f"{name[0]} {name[1]} | {idt} | {number_of_penalties[-1]}\n"

    return message_to_send


async def all_users_penalties_show(callback_message, state: FSMContext):
    if isinstance(callback_message, types.Message):
        await callback_message.answer(form_the_message_with_penalties(),
                                      reply_markup=keyboards.keyboard_back_to_main_teacher())
        await state.update_data(prev_msg_id=callback_message.message_id)

    if isinstance(callback_message, types.CallbackQuery):
        await callback_message.message.edit_text(form_the_message_with_penalties(),
                                                 reply_markup=keyboards.keyboard_back_to_main_teacher())
        await state.update_data(prev_msg_id=callback_message.message.message_id)

    await state.set_state(ShowClientPenaltyCard.get_client_id)


async def penalty_card(message, state, bot, idt):
    query = database.fetchall_multiple("select reason, id from penalty where idt=?", (idt,))

    print(idt)

    message_to_send = "<b>ID | Причина</b>\n"
    await message.delete()

    if len(query) != 0:
        for penalty in query:
            message_to_send += f"{penalty[1]} | {penalty[0]}\n"
        await message.answer(message_to_send, reply_markup=keyboards.keyboard_penalty_card_teacher())
    else:
        await message.answer(TeacherMessages.NO_PENALTIES, reply_markup=keyboards.keyboard_penalty_card_teacher())

    await state.update_data(prev_msg_id=message.message_id)
    await state.set_state(ShowClientPenaltyCard.further_actions)


@router.callback_query(F.data == "penalty")
async def penalty(callback: types.CallbackQuery, state: FSMContext):
    await all_users_penalties_show(callback, state)


@router.message(F.text, ShowClientPenaltyCard.get_client_id)
async def show_penalty_card(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data['prev_msg_id'])
    await penalty_card(message, state, bot, message.text)
    await state.update_data(idt=message.text)


@router.callback_query(F.data == "add_penalty", ShowClientPenaltyCard.further_actions)
async def add_penalty(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.edit_text(TeacherMessages.ENTER_PENALTY_REASON)
    await state.set_state(ShowClientPenaltyCard.get_penalty_reasons)


@router.message(F.text, ShowClientPenaltyCard.get_penalty_reasons)
async def insert_new_penalty(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    reasons = message.text
    to_add = [data['idt'], reasons]
    database.execute("Insert into penalty values (NULL, ?, ? )", to_add)
    await message.answer(TeacherMessages.PENALTY_ADDED)
    await penalty_card(message, state, bot, data['idt'])


@router.callback_query(F.data == "remove_penalty", ShowClientPenaltyCard.further_actions)
async def remove_penalty(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.answer(TeacherMessages.ENTER_PENALTY_ID_TO_DELETE)
    await state.update_data(msg_to_delete=[callback.message.message_id])
    await state.set_state(ShowClientPenaltyCard.get_penalty_id_to_delete)


@router.message(F.text, ShowClientPenaltyCard.get_penalty_id_to_delete)
async def remove_penalty_delete(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if not message.text.isdigit():
        await message.answer(TeacherMessages.ONLY_NUMBERS_ALLOWED)
        return remove_penalty_delete

    database.execute("delete from penalty where id=?", (message.text,))

    for msg in data['msg_to_delete']:
        await bot.delete_message(message.from_user.id, msg)

    await message.answer(TeacherMessages.PENALTY_DELETED)
    await penalty_card(message, state, bot, data['idt'])


@router.callback_query(F.data == CallbackDataKeys.back_to_penalties_teacher)
async def back_to_penalties_teacher(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await all_users_penalties_show(callback, state)
