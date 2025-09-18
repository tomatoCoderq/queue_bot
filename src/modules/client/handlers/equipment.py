from aiogram import Dispatcher, F, Router, types
from aiogram.fsm.context import FSMContext

from src.modules.shared.callbacks import CallbackDataKeys
from src.modules.client.manager import ClientManagerEquipment
from src.modules.models.client import Client

router = Router()
dp = Dispatcher()


@router.callback_query(F.data == CallbackDataKeys.STUDENT_EQUIPMENT)
async def show_inventory(callback: types.CallbackQuery, state: FSMContext):
    client = Client(callback.from_user.id)
    manager = ClientManagerEquipment(client)
    await manager.show_inventory(callback, state)


# @router.callback_query(F.data == CallbackDataKeys.BACK_TO_MAIN)
# async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
#     client = Client(callback.from_user.id)
#     manager = ClientManagerEquipment(client)
#     await manager.back_to_menu(callback, state)
