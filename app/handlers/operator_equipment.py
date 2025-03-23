import random
from typing import *
import os
import datetime

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command
from exceptiongroup import catch

from app.fsm_states.operator_states import ItemActionState, AliasLookupState, InventoryAddState
from app.managers.operator_manager import OperatorManagerEquipment
# from app.utils.files import *


from app.utils import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter

from app.utils.database import database
from app.utils.keyboards import CallbackDataKeys
# from main import dp
from app.handlers.operator_details import Operator
from app.utils.filters import IsStudent
from app.utils.messages import StudentMessages

router = Router()
dp = Dispatcher()


@router.callback_query(F.data.in_({"back_to_inventory", "teacher_equipment"}))
async def show_bucket_handler(callback: types.CallbackQuery, state: FSMContext):
    operator = Operator(callback.from_user.id)
    manager = OperatorManagerEquipment(operator)
    await manager.show_bucket(callback, state)


@router.callback_query(F.data == "inventory_add")
async def inventory_add_start_handler(callback: types.CallbackQuery, state: FSMContext):
    operator = Operator(callback.from_user.id)
    manager = OperatorManagerEquipment(operator)
    await manager.inventory_add_start(callback, state)


@router.message(InventoryAddState.waiting_for_detail_info, F.text)
async def process_inventory_add_handler(message: types.Message, state: FSMContext):
    operator = Operator(message.from_user.id)
    manager = OperatorManagerEquipment(operator)
    await manager.process_inventory_add(message, state)

# Add code inside show_bucket to another function to get the list of all availible details from everywhere

# async def form_message_with_bucket(callback: Union[types.CallbackQuery, types.Message], state: FSMContext):
#     operator = OperatorDetails(str(callback.from_user.id))
#     details_list = operator.get_all_details()
#
#     detail_groups = {}
#     for detail in details_list:
#         detail_groups.setdefault(detail.name, []).append(detail)
#
#     summary_lines = []
#     for name, items in detail_groups.items():
#         alias_result = database.fetchall("SELECT alias FROM detail_aliases WHERE name=?", (name,))
#         alias = alias_result[0] if alias_result else name[:5].upper()
#         summary_lines.append(f"🔸 <b>{alias}</b> (<i>{name}</i>): <b>{len(items)}</b> шт.")
#     summary = "\n".join(summary_lines) if summary_lines else "<b>Нет деталей в инвентаре.</b>"
#
#     if isinstance(callback, types.CallbackQuery):
#         await callback.message.edit_text(summary, parse_mode=ParseMode.HTML, reply_markup=keyboard_inventory())
#     else:
#         await callback.answer(summary, parse_mode=ParseMode.HTML, reply_markup=keyboard_inventory())
#



# async def form_message_detail_info(message: types.Message, state: FSMContext, details):
#     cost = details[0][2]  # Assuming the price is stored at index 2.
#     owner_name_map = Operator.get_idt_name_map()
#
#     output_lines = [f"💰 <b>Цена:</b> {cost}", "📦 <b>Объекты:</b>"]
#     for detail in details:
#         obj_id = detail[0]
#         owner_id = detail[3]
#         if owner_id and owner_id in owner_name_map:
#             owner_name = f"{owner_name_map[owner_id][0]} {owner_name_map[owner_id][1]}"
#         else:
#             owner_name = "Нет владельца"
#         output_lines.append(f"🔹 <b>ID:</b> {obj_id} | <b>Владелец:</b> {owner_name}")
#
#     output = "\n".join(output_lines)
#     return output

@router.message(AliasLookupState.waiting_for_alias, F.text)
async def process_alias_lookup_handler(message: types.Message, state: FSMContext):
    operator = Operator(message.from_user.id)
    manager = OperatorManagerEquipment(operator)
    await manager.process_alias_lookup(message, state)


@router.callback_query(F.data == "transfer_item")
async def transfer_item_handler(callback: types.CallbackQuery, state: FSMContext):
    operator = Operator(callback.from_user.id)
    manager = OperatorManagerEquipment(operator)
    await manager.transfer_item(callback, state)


@router.message(ItemActionState.waiting_for_transfer_info, F.text)
async def process_transfer_item_handler(message: types.Message, state: FSMContext):
    operator = Operator(message.from_user.id)
    manager = OperatorManagerEquipment(operator)
    await manager.process_transfer_item(message, state)


@router.callback_query(F.data == "return_item")
async def return_item_handler(callback: types.CallbackQuery, state: FSMContext):
    operator = Operator(callback.from_user.id)
    manager = OperatorManagerEquipment(operator)
    await manager.return_item(callback, state)


@router.message(ItemActionState.waiting_for_return_info, F.text)
async def process_return_item_handler(message: types.Message, state: FSMContext):
    operator = Operator(message.from_user.id)
    manager = OperatorManagerEquipment(operator)
    await manager.process_return_item(message, state)


@router.callback_query(F.data == "back_to_main")
async def back_to_main_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Главное меню</b>",
        reply_markup=keyboards.keyboard_main_teacher(),
        parse_mode=ParseMode.HTML
    )
    await state.clear()
