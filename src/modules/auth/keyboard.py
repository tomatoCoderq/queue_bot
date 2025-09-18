"""Keyboards for registration and authentication flows."""

from aiogram import types

from src.modules.shared.callbacks import CallbackDataKeys
from src.modules.shared.messages import KeyboardTitles


def keyboard_start_registration() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.start_registration_client,
                                    callback_data=CallbackDataKeys.start_registration_client)],
        [types.InlineKeyboardButton(text=KeyboardTitles.start_registration_operator,
                                    callback_data=CallbackDataKeys.start_registration_operator)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
