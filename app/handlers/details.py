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


class AliasLookupState(StatesGroup):
    waiting_for_alias = State()


class Detail:
    def __init__(self, name: str, price: float, detail_id: int = random.randint(1000, 9999)):
        self.name = name
        self.price = price
        self.detail_id: int = detail_id

    def __str__(self):
        return f"{self.detail_id} {self.name} {self.price}"

    def change_price(self, price: float):
        self.price = price

    def change_name(self, name: str):
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

        self.bucket = Bucket  # Note: assign Bucket class or an instance if desired

    def __show_list_of_details(self):
        # Retrieve details owned by this client from the database.
        details = database.fetchall_multiple("SELECT * FROM details WHERE owner=?", (self.telegram_id,))
        details_list: List[Detail] = list()
        for detail in details:
            details_list.append(Detail(
                name=detail[1],
                price=detail[2],
                detail_id=detail[0]
            ))
        return details_list


class OperatorDetails:
    def __init__(self, telegram_id: str):
        self.telegram_id = telegram_id
        self.bucket = Bucket()

    @staticmethod
    def __generate_alias(name: str) -> str:
        vowels = "aeiouAEIOU"
        words = name.split()
        if len(words) >= 2:
            # Take first 3 letters of the first word.
            first_part = words[0][:3].upper() if len(words[0]) >= 3 else words[0].upper()
            # For the second word, take the first letter plus the first non-vowel after it.
            second_word = words[1]
            second_part = second_word[0].upper()
            for ch in second_word[1:]:
                if ch not in vowels:
                    second_part += ch.upper()
                    break
            return first_part + second_part
        else:
            # For a single-word name, simply take the first 5 characters.
            return name[:5].upper()

    def __form_message_with_details(self):
        details_list = self.get_all_details()
        formed_string = ""
        for detail in details_list:
            # Placeholder for further grouping or formatting.
            pass

    @staticmethod
    def add_details_to_bucket(detail: Detail):
        alias = OperatorDetails.__generate_alias(detail.name)

        existing = database.fetchall("SELECT alias FROM detail_aliases WHERE name=?", (detail.name,))
        if not existing:
            database.execute("INSERT INTO detail_aliases VALUES (?, ?)", (detail.name, alias))

        database.execute("INSERT INTO details VALUES (NULL, ?, ?, NULL)", (detail.name, detail.price))

    def remove_details_from_bucket(self, detail_id: str):
        database.execute("DELETE FROM details WHERE id=?", (detail_id,))

    def get_all_details(self) -> List[Detail]:
        details = database.fetchall_multiple("SELECT * FROM details")
        details_list: List[Detail] = list()
        for detail in details:
            details_list.append(Detail(
                name=detail[1],
                price=detail[2],
                detail_id=detail[0]
            ))
        return details_list

    def move_detail_to_client(self, detail_id: str, client_telegram_id: str):
        database.execute("UPDATE details SET owner=? WHERE id=?", (client_telegram_id, detail_id))

    def take_detail_from_client(self, detail_id: str):
        database.execute("UPDATE details SET owner=NULL WHERE id=?", (detail_id,))


def keyboard_inventory():
    buttons = [
        [types.InlineKeyboardButton(text="➕ Добавить", callback_data="inventory_add")],
        # [types.InlineKeyboardButton(text="🛒 Корзина", callback_data="inventory_bucket")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_alias_back():
    buttons = [
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_inventory")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_transfer_return():
    buttons = [
        [types.InlineKeyboardButton(text="🔄 Передать", callback_data="transfer_item")],
        [types.InlineKeyboardButton(text="↩️ Вернуть", callback_data="return_item")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_inventory")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


class InventoryAddState(StatesGroup):
    waiting_for_detail_info = State()


def detail_exists(detail_id: int) -> bool:
    """Check if a detail with the given ID exists in the details table."""
    result = database.fetchall("SELECT id FROM details WHERE id=?", (detail_id,))
    return bool(result)


def user_exists(user_id: int) -> bool:
    """Check if a user with the given ID exists in the users table."""
    result = database.fetchall("SELECT idt FROM users WHERE idt=?", (user_id,))
    return bool(result)


@router.callback_query(F.data == "inventory_add")
async def inventory_add_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Введите название детали</b> и <b>цену</b> через запятую.\nПример: <i>Arduino Mega, 1500</i>",
        reply_markup=keyboard_alias_back(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(InventoryAddState.waiting_for_detail_info)


@router.message(InventoryAddState.waiting_for_detail_info, F.text)
async def process_inventory_add(message: types.Message, state: FSMContext):
    text = message.text
    try:
        # Expect input format: "Название, цена"
        name, price_str = [part.strip() for part in text.split(",", 1)]
        price = float(price_str)
    except Exception as e:
        await message.answer(
            "<b>Неверный формат!</b> Введите данные в формате: <i>Название, цена</i>",
            parse_mode=ParseMode.HTML
        )
        return

    new_detail = Detail(name=name, price=price)
    OperatorDetails.add_details_to_bucket(detail=new_detail)

    await message.answer(
        f"✅ Деталь «<b>{name}</b>» успешно добавлена со стоимостью <b>{price}</b>.",
        reply_markup=keyboard_inventory(),
        parse_mode=ParseMode.HTML
    )
    await state.clear()

# Add code inside show_bucket to another function to get the list of all availible details from everywhere

async def form_message_with_bucket(callback: Union[types.CallbackQuery, types.Message], state: FSMContext):
    operator = OperatorDetails(str(callback.from_user.id))
    details_list = operator.get_all_details()

    detail_groups = {}
    for detail in details_list:
        detail_groups.setdefault(detail.name, []).append(detail)

    summary_lines = []
    for name, items in detail_groups.items():
        alias_result = database.fetchall("SELECT alias FROM detail_aliases WHERE name=?", (name,))
        alias = alias_result[0] if alias_result else name[:5].upper()
        summary_lines.append(f"🔸 <b>{alias}</b> (<i>{name}</i>): <b>{len(items)}</b> шт.")
    summary = "\n".join(summary_lines) if summary_lines else "<b>Нет деталей в инвентаре.</b>"

    if isinstance(callback, types.CallbackQuery):
        await callback.message.edit_text(summary, parse_mode=ParseMode.HTML, reply_markup=keyboard_inventory())
    else:
        await callback.answer(summary, parse_mode=ParseMode.HTML, reply_markup=keyboard_inventory())


@router.callback_query(F.data.in_({"back_to_inventory", "teacher_equipment"}))
async def show_bucket(callback: types.CallbackQuery, state: FSMContext):
    operator = OperatorDetails(str(callback.from_user.id))
    # Assume operator.bucket is an instance of Bucket.
    # bucket_details = operator.bucket  # Use the Bucket instance.
    # if not bucket_details or not bucket_details.get_details():
    #     text = "<b>Ваша корзина пуста.</b>"
    # else:
    #     lines = []
    #     for detail in bucket_details.get_details():
    #         lines.append(f"🔹 <b>ID:</b> {detail.detail_id} – <b>{detail.name}</b> (<b>Цена:</b> {detail.price})")
    #     text = "<b>Корзина:</b>\n" + "\n".join(lines)
    # await callback.message.edit_text(text, reply_markup=keyboard_inventory())

    await form_message_with_bucket(callback, state)
    # await state.clear()
    #
    # # Show a summary grouped by detail name.
    # operator = OperatorDetails(str(callback.from_user.id))
    # details_list = operator.get_all_details()
    #
    # detail_groups = {}
    # for detail in details_list:
    #     detail_groups.setdefault(detail.name, []).append(detail)
    #
    # summary_lines = []
    # for name, items in detail_groups.items():
    #     alias_result = database.fetchall("SELECT alias FROM detail_aliases WHERE name=?", (name,))
    #     alias = alias_result[0] if alias_result else name[:5].upper()
    #     summary_lines.append(f"🔸 <b>{alias}</b> (<i>{name}</i>): <b>{len(items)}</b> шт.")
    # summary = "\n".join(summary_lines) if summary_lines else "<b>Нет деталей в инвентаре.</b>"
    #
    # await callback.message.edit_text(summary, parse_mode=ParseMode.HTML, reply_markup=keyboard_inventory())
    await state.set_state(AliasLookupState.waiting_for_alias)


async def form_message_detail_info(message: types.Message, state: FSMContext, details):
    cost = details[0][2]  # Assuming the price is stored at index 2.
    owner_name_map = Operator.get_idt_name_map()

    output_lines = [f"💰 <b>Цена:</b> {cost}", "📦 <b>Объекты:</b>"]
    for detail in details:
        obj_id = detail[0]
        owner_id = detail[3]
        if owner_id and owner_id in owner_name_map:
            owner_name = f"{owner_name_map[owner_id][0]} {owner_name_map[owner_id][1]}"
        else:
            owner_name = "Нет владельца"
        output_lines.append(f"🔹 <b>ID:</b> {obj_id} | <b>Владелец:</b> {owner_name}")

    output = "\n".join(output_lines)
    return output

@router.message(AliasLookupState.waiting_for_alias, F.text)
async def process_alias_lookup(message: types.Message, state: FSMContext):
    user_alias = message.text.strip().upper()

    result = database.fetchall("SELECT name FROM detail_aliases WHERE alias=?", (user_alias,))
    if not result:
        await message.answer(
            "❌ <b>Ошибка:</b> Объект с алиасом <i>{}</i> не найден.".format(user_alias),
            reply_markup=keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        return

    full_name = result[0]

    details = database.fetchall_multiple("SELECT id, name, price, owner FROM details WHERE name=?", (full_name,))
    if not details:
        await message.answer(
            "❌ <b>Ошибка:</b> Нет деталей с именем <i>{}</i> в инвентаре.".format(full_name),
            reply_markup=keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        return

    output = await form_message_detail_info(message, state, details)

    await message.answer(output, reply_markup=keyboard_transfer_return(), parse_mode=ParseMode.HTML)
    await state.clear()


class ItemActionState(StatesGroup):
    waiting_for_transfer_info = State()
    waiting_for_return_info = State()


@router.callback_query(F.data == "transfer_item")
async def start_transfer_item(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите <b>ID объекта</b> и <b>ID нового владельца</b> через запятую.\nПример: <i>23, 987654321</i>",
        reply_markup=keyboard_alias_back(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(ItemActionState.waiting_for_transfer_info)


@router.message(ItemActionState.waiting_for_transfer_info, F.text)
async def process_transfer_item(message: types.Message, state: FSMContext):
    try:
        obj_id_str, new_owner_str = [part.strip() for part in message.text.split(",", 1)]
        obj_id = int(obj_id_str)
        new_owner = int(new_owner_str)
    except ValueError:
        await message.answer(
            "❌ <b>Ошибка:</b> Введите корректные числа в формате: <i>ID объекта, ID нового владельца</i>.",
            reply_markup=keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        return

    if not detail_exists(obj_id):
        await message.answer(
            f"❌ <b>Ошибка:</b> Объект с ID <b>{obj_id}</b> не найден в инвентаре.",
            reply_markup=keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        return

    if not user_exists(new_owner):
        await message.answer(
            f"❌ <b>Ошибка:</b> Пользователь с ID <b>{new_owner}</b> не найден в системе.",
            reply_markup=keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        return

    database.execute("UPDATE details SET owner=? WHERE id=?", (new_owner, obj_id))
    await message.answer(
        f"✅ Объект с ID <b>{obj_id}</b> успешно передан пользователю <b>{new_owner}</b>.",
        reply_markup=keyboard_transfer_return(),
        parse_mode=ParseMode.HTML
    )
    await form_message_with_bucket(message, state)
    await state.set_state(AliasLookupState.waiting_for_alias)


@router.callback_query(F.data == "return_item")
async def start_return_item(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите <b>ID объекта</b> для возврата.\nПример: <i>23</i>",
        reply_markup=keyboard_alias_back(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(ItemActionState.waiting_for_return_info)


@router.message(ItemActionState.waiting_for_return_info, F.text)
async def process_return_item(message: types.Message, state: FSMContext):
    try:
        obj_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ <b>Ошибка:</b> Введите корректный числовой ID объекта.",
            reply_markup=keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        return

    if not detail_exists(obj_id):
        await message.answer(
            f"❌ <b>Ошибка:</b> Объект с ID <b>{obj_id}</b> не найден в инвентаре.",
            reply_markup=keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        return

    database.execute("UPDATE details SET owner=NULL WHERE id=?", (obj_id,))
    await message.answer(
        f"✅ Объект с ID <b>{obj_id}</b> успешно возвращён в инвентарь.",
        reply_markup=keyboard_transfer_return(),
        parse_mode=ParseMode.HTML
    )
    await state.clear()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Главное меню</b>",
        reply_markup=keyboards.keyboard_main_teacher(),
        parse_mode=ParseMode.HTML
    )
    await state.clear()
