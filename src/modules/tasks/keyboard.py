"""Keyboards for task management flows."""

from aiogram import types

from src.modules.shared.callbacks import CallbackDataKeys
from src.modules.shared.messages import KeyboardTitles


def keyboard_process_end_of_session_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.confirm_high_urgency,
                                    callback_data=CallbackDataKeys.accept_end_of_session)],
        [types.InlineKeyboardButton(text=KeyboardTitles.reject_high_urgency,
                                    callback_data=CallbackDataKeys.reject_end_of_session)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_process_high_urgency_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.confirm_high_urgency,
                                    callback_data=CallbackDataKeys.confirm_high_urgency)],
        [types.InlineKeyboardButton(text=KeyboardTitles.reject_high_urgency,
                                    callback_data=CallbackDataKeys.reject_high_urgency)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_process_submit_task_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.confirm_high_urgency,
                                    callback_data=CallbackDataKeys.accept_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.reject_high_urgency,
                                    callback_data=CallbackDataKeys.reject_task)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
