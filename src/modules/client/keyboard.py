"""Keyboards for client-facing flows."""

from aiogram import types

from src.modules.shared.callbacks import CallbackDataKeys
from src.modules.shared.messages import KeyboardTitles


def keyboard_main_student() -> types.InlineKeyboardMarkup:
    """Main menu keyboard for students."""
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.upload_detail, callback_data=CallbackDataKeys.upload_detail)],
        [types.InlineKeyboardButton(text=KeyboardTitles.task_queue, callback_data=CallbackDataKeys.details_queue)],
        [types.InlineKeyboardButton(text=KeyboardTitles.tasks, callback_data=CallbackDataKeys.tasks)],
        [types.InlineKeyboardButton(text="📦Комплектующие", callback_data=CallbackDataKeys.STUDENT_EQUIPMENT)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_submit_tasks_student() -> types.InlineKeyboardMarkup:
    """Keyboard for task submission options."""
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.submit_tasks, callback_data=CallbackDataKeys.submit_tasks)],
        [types.InlineKeyboardButton(text=KeyboardTitles.close_tasks, callback_data=CallbackDataKeys.close_tasks)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_student,
                                    callback_data=CallbackDataKeys.back_to_main_student)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_end_of_hour_check_student() -> types.InlineKeyboardMarkup:
    """Keyboard for end of hour task management."""
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.end_current_task,
                                    callback_data=CallbackDataKeys.end_current_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.continue_current_task,
                                    callback_data=CallbackDataKeys.continue_current_task)],
        [
            types.InlineKeyboardButton(text=KeyboardTitles.add_10_minutes,
                                       callback_data=CallbackDataKeys.add_10_minutes),
            types.InlineKeyboardButton(text=KeyboardTitles.add_15_minutes,
                                       callback_data=CallbackDataKeys.add_15_minutes),
            types.InlineKeyboardButton(text=KeyboardTitles.add_30_minutes,
                                       callback_data=CallbackDataKeys.add_30_minutes),
        ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_urgency_student() -> types.InlineKeyboardMarkup:
    """Keyboard for urgency selection."""
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.urgency_high, callback_data=CallbackDataKeys.urgency_high)],
        [types.InlineKeyboardButton(text=KeyboardTitles.urgency_medium, callback_data=CallbackDataKeys.urgency_medium)],
        [types.InlineKeyboardButton(text=KeyboardTitles.urgency_low, callback_data=CallbackDataKeys.urgency_low)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_student,
                                    callback_data=CallbackDataKeys.back_to_main_student)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_back_to_main_student() -> types.InlineKeyboardMarkup:
    """Simple back to main keyboard for students."""
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_student,
                                    callback_data=CallbackDataKeys.back_to_main_student)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_alias_back_student() -> types.InlineKeyboardMarkup:
    """Back button for student equipment."""
    buttons = [
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_inventory_student")],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
