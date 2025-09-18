from aiogram import F, Router, types
from aiogram.enums import ContentType, ParseMode
from aiogram.fsm.context import FSMContext

from src.fsm_states.client_states import SendPiece
from src.fsm_states.operator_states import CheckMessage, ReturnToQueue, ShowClientCard
from src.modules.operator.handlers.students_cards import get_student_selection_keyboard
from src.modules.client import keyboard as client_keyboard
from src.modules.operator import keyboard as operator_keyboard
from src.modules.tasks import keyboard as tasks_keyboard

BACK_ROUTE_MAP = {
    # ─── CLIENT ROUTES ─────────────────────────────────────────────────────────
    "back_to_main_student": {
        "text": "<b>Выбирайте, Клиент!</b>",
        "keyboard": client_keyboard.keyboard_main_student,
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
        "keyboard": client_keyboard.keyboard_main_student,
        "clear": True,
        "edit": True
    },

    # ─── OPERATOR ROUTES ───────────────────────────────────────────────────────
    "back_to_main_teacher": {
        "text": "<b>Выбирайте, Оператор!</b>",
        "keyboard": operator_keyboard.keyboard_main_teacher,
        "clear": True,
        "edit": True
    },
    "back_to_queue": {
        "text": "<b>Очередь заявок</b>",
        "keyboard": operator_keyboard.keyboard_details_teacher,
        "state": CheckMessage.waiting_id,
        "clear": False,
        "edit": True
    },
    "back_to_details_teacher": {
        "text": "<b>Выберите действие</b>",
        "keyboard": operator_keyboard.keyboard_details_teacher,
        "clear": True,
        "edit": True

    },
    "back_to_details_teacher_no_edit": {
        "text": "<b>Выберите действие</b>",
        "keyboard": operator_keyboard.keyboard_details_teacher,
        "clear": True,
        "edit": False
    },
    "back_to_penalties_teacher": {
        "text": "<b>Выберите ученика</b>",
        "keyboard": operator_keyboard.keyboard_back_to_details_teacher,
        "state": ShowClientCard.get_client_id,
        "clear": False
    },
    "back_to_history": {
        "text": "<b>История заявок</b>\nНапишите ID, чтобы вернуть заявку в очередь.",
        "keyboard": operator_keyboard.keyboard_back_to_details_teacher,
        "state": ReturnToQueue.waiting_id,
        "clear": False,
        "edit": True
    },
    "back_to_inventory": {
        "text": "<b>Выбирайте, Оператор!</b>",
        "keyboard": operator_keyboard.keyboard_main_teacher,  # Or custom inventory keyboard if needed
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
