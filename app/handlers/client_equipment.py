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

from app.models.client import Client
from app.managers.client_manager import ClientManagerEquipment
from app.utils import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter

from app.utils.database import database
from app.utils.keyboards import CallbackDataKeys
from app.models.client import Client
from app.utils.messages import KeyboardTitles, StudentMessages

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
