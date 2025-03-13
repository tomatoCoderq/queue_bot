from aiogram.fsm.context import FSMContext
from aiogram import F, Dispatcher

from app.managers.operator_manager import OperatorManagerPenalties
from app.models.operator import Operator
from aiogram import Bot, types, Router

from app.utils.keyboards import CallbackDataKeys
from app.fsm_states.operator_states import ShowClientPenaltyCard

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

router = Router()
dp = Dispatcher()


@router.callback_query(F.data == "penalty")
async def penalty_handler(callback: types.CallbackQuery, state: FSMContext):
    teacher = Operator(callback.from_user.id, callback.from_user.username)
    manager = OperatorManagerPenalties(teacher)
    await manager.all_users_penalties_show(callback, state)
    # await all_users_penalties_show(callback, state)


@router.message(F.text, ShowClientPenaltyCard.get_client_id)
async def show_penalty_card_handler(message: types.Message, state: FSMContext, bot: Bot):
    teacher = Operator(message.from_user.id, message.from_user.username)
    manager = OperatorManagerPenalties(teacher)
    await manager.show_penalty_card(message, state, bot)


@router.callback_query(F.data == "add_penalty", ShowClientPenaltyCard.further_actions)
async def add_penalty_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    teacher = Operator(callback.from_user.id, callback.from_user.username)
    manager = OperatorManagerPenalties(teacher)
    await manager.add_penalty(callback, state)


@router.message(F.text, ShowClientPenaltyCard.get_penalty_reasons)
async def insert_added_penalty_handler(message: types.Message, state: FSMContext, bot: Bot):
    teacher = Operator(message.from_user.id, message.from_user.username)
    manager = OperatorManagerPenalties(teacher)
    await manager.insert_added_penalty(message, state, bot)


@router.callback_query(F.data == "remove_penalty", ShowClientPenaltyCard.further_actions)
async def remove_penalty_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    teacher = Operator(callback.from_user.id, callback.from_user.username)
    manager = OperatorManagerPenalties(teacher)
    await manager.remove_penalty(callback, state, bot)


@router.message(F.text, ShowClientPenaltyCard.get_penalty_id_to_delete)
async def delete_removed_penalty_handler(message: types.Message, state: FSMContext, bot: Bot):
    teacher = Operator(message.from_user.id, message.from_user.username)
    manager = OperatorManagerPenalties(teacher)
    await manager.delete_removed_penalty(message, state, bot)


@router.callback_query(F.data == CallbackDataKeys.back_to_penalties_teacher)
async def back_to_penalties_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    teacher = Operator(callback.from_user.id, callback.from_user.username)
    manager = OperatorManagerPenalties(teacher)
    await manager.all_users_penalties_show(callback, state)

