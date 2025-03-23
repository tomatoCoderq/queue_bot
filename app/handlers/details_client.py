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

from app.utils import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter

from app.utils.database import database
from app.utils.keyboards import CallbackDataKeys
from app.utils.messages import KeyboardTitles, StudentMessages

router = Router()
dp = Dispatcher()


class Detail:

    def __init__(self, name: str, price: float, detail_id: int = random.randint(1000, 9999)):
        self.name = name
        self.price = price
        self.detail_id: int = detail_id

    def __str__(self):
        return str(self.detail_id) + " " + self.name + " " + str(self.price)

    def change_price(self, price: float):
        self.price = price

    def change_name(self, name):
        self.name = name

    def get_id(self) -> int:
        return self.detail_id


class Bucket:
    def __init__(self):
        self.__bucket_array: List[Detail] = list()

    def add_detail(self, detail: Detail):
        self.__bucket_array.append(detail)

    def remove_detail(self, detail_id: int):
        for detail in self.__bucket_array:
            if detail.get_id() == detail_id:
                self.__bucket_array.remove(detail)

    def get_details(self):
        return self.__bucket_array


class Client:
    def __init__(self, name: str, surname: str, telegram_id: str):
        self.name = name
        self.surname = surname
        self.telegram_id = telegram_id

        self.bucket = Bucket

    def __show_list_of_details(self):
        # Here we get from bd data of details with owner
        details = database.fetchall_multiple("SELECT * from details where owner=?", (self.telegram_id,))
        details_list: List[Detail] = list()
        for detail in details:
            details_list.append(Detail(
                name=detail[1],
                price=detail[2],
                detail_id=detail[0])
            )
        return details_list


@router.callback_query(F.data == CallbackDataKeys.STUDENT_EQUIPMENT)
async def show_inventory(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    details = database.fetchall_multiple("SELECT * FROM details WHERE owner = ?", (user_id,))

    if not details:
        await callback.message.answer(
            StudentMessages.NO_EQUIPMENT_FOUND,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard_alias_back()
        )
    else:
        equipment_message = StudentMessages.YOUR_EQUIPMENT_HEADER
        for detail in details:
            detail_id, name, price, owner = detail
            equipment_message += StudentMessages.EQUIPMENT_ITEM_FORMAT.format(
                detail_id=detail_id, name=name, price=price)
        await callback.message.edit_text(
            equipment_message,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard_alias_back()
        )
    await callback.answer()


@router.callback_query(F.data == CallbackDataKeys.BACK_TO_MAIN)
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        StudentMessages.choose_next_action,
        reply_markup=keyboards.keyboard_main_student(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


def keyboard_inventory():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.ADD_DETAIL, callback_data=CallbackDataKeys.INVENTORY_ADD)],
        [types.InlineKeyboardButton(text=KeyboardTitles.BACK, callback_data=CallbackDataKeys.BACK_TO_MAIN)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_alias_back():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text=KeyboardTitles.BACK, callback_data=CallbackDataKeys.BACK_TO_INVENTORY)]]
    )
