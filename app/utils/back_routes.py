from app.handlers.operator_students_cards import get_student_selection_keyboard
from app.utils.keyboards import keyboard_main_student, keyboard_main_teacher

import asyncio
import os
import datetime
import time

from aiogram.enums import ParseMode, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command

from app.handlers.test_handlers import update
from app.utils import keyboards
from app.utils.keyboards import *
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter
import aioschedule

from app.utils.database import database
from app.utils.keyboards import CallbackDataKeys
# from main import dp
# from app.handlers.teacher import create_idt_name_map
from app.utils.filters import IsStudent
from app.fsm_states.client_states import SendPiece
from app.fsm_states.operator_states import CheckMessage, ShowClientCard, ReturnToQueue
from app.utils.messages import StudentMessages

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.handlers.add_tasks import is_any_task

BACK_ROUTE_MAP = {
    # ─── CLIENT ROUTES ─────────────────────────────────────────────────────────
    "back_to_main_student": {
        "text": "<b>Выбирайте, Клиент!</b>",
        "keyboard": keyboard_main_student,
        "clear": True,
        "edit": True
    },
    "back_to_upload_file": {
        "text": "<b>Прикрепите файл снова</b>",
        "keyboard": None,
        "state": SendPiece.waiting_file,
        "clear": False,
        "edit": True
    },
    "back_to_inventory_student": {
        "text": "<b>Выбирайте, Клиент!</b>",
        "keyboard": keyboard_main_student,
        "clear": True,
        "edit": True
    },

    # ─── OPERATOR ROUTES ───────────────────────────────────────────────────────
    "back_to_main_teacher": {
        "text": "<b>Выбирайте, Оператор!</b>",
        "keyboard": keyboard_main_teacher(),
        "clear": True,
        "edit": True
    },
    "back_to_queue": {
        "text": "<b>Очередь заявок</b>",
        "keyboard": keyboard_details_teacher,
        "state": CheckMessage.waiting_id,
        "clear": False,
        "edit": True
    },
    "back_to_details_teacher": {
        "text": "<b>Выберите действие</b>",
        "keyboard": keyboard_details_teacher,
        "clear": True,
        "edit": True

    },
    "back_to_details_teacher_no_edit": {
        "text": "<b>Выберите действие</b>",
        "keyboard": keyboard_details_teacher,
        "clear": True,
        "edit": False
    },
    "back_to_penalties_teacher": {
        "text": "<b>Выберите ученика</b>",
        "keyboard": keyboard_back_to_details_teacher,
        "state": ShowClientCard.get_client_id,
        "clear": False
    },
    "back_to_history": {
        "text": "<b>История заявок</b>\nНапишите ID, чтобы вернуть заявку в очередь.",
        "keyboard": keyboard_back_to_details_teacher,
        "state": ReturnToQueue.waiting_id,
        "clear": False,
        "edit": True
    },
    "back_to_inventory": {
        "text": "<b>Выбирайте, Оператор!</b>",
        "keyboard": keyboard_main_teacher,  # Or custom inventory keyboard if needed
        "clear": True,
        "edit": True
    },
    "back_to_list_of_students": {
        "text": "<b>Выберите ученика!</b>",
        "keyboard": get_student_selection_keyboard,  # Or custom inventory keyboard if needed
        "state": ShowClientCard.get_client_id,
        "clear": False,
        "edit": True
    },
}


router = Router()
dp = Dispatcher()


@router.callback_query(F.data.startswith("back_to_"))
async def back_handler(callback: types.CallbackQuery, state: FSMContext):
    print("here", callback.data)
    route = BACK_ROUTE_MAP.get(callback.data)

    if not route:
        await callback.answer("❌ Назад невозможно.")
        return

    if route.get("clear"):
        await state.clear()
    elif "state" in route:
        await state.set_state(route["state"])

    keyboard = route["keyboard"]() if callable(route.get("keyboard")) else route.get("keyboard")

    if callback.message.content_type != ContentType.TEXT:
        await callback.message.delete()
        await callback.message.answer(
            route["text"],
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await callback.message.edit_text(
            route["text"],
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    await callback.answer()