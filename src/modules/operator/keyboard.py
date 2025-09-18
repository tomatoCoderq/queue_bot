"""Keyboards for operator-facing flows."""

from aiogram import types

from src.modules.shared.callbacks import CallbackDataKeys
from src.modules.shared.messages import KeyboardTitles


def keyboard_main_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.details_queue_teacher,
                                    callback_data=CallbackDataKeys.details_queue_teacher)],
        [types.InlineKeyboardButton(text="👦🏻Клиенты", callback_data=CallbackDataKeys.clients)],
        [types.InlineKeyboardButton(text="📦Комплектующие", callback_data="teacher_equipment")],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_details_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.open_queue, callback_data=CallbackDataKeys.open_queue)],
        [types.InlineKeyboardButton(text=KeyboardTitles.history, callback_data=CallbackDataKeys.history)],
        [types.InlineKeyboardButton(text=KeyboardTitles.get_xlsx, callback_data=CallbackDataKeys.xlsx)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_queue,
                                    callback_data=CallbackDataKeys.back_to_main_teacher)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_sort_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.sort_by_type, callback_data=CallbackDataKeys.sort_by_type)],
        [types.InlineKeyboardButton(text=KeyboardTitles.sort_by_date, callback_data=CallbackDataKeys.sort_by_date)],
        [types.InlineKeyboardButton(text=KeyboardTitles.sort_by_urgency,
                                    callback_data=CallbackDataKeys.sort_by_urgency)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_details_teacher)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_teacher_actions_one() -> types.InlineKeyboardMarkup:
    buttons = [
        [
            types.InlineKeyboardButton(text=KeyboardTitles.accept_task, callback_data=CallbackDataKeys.accept_detail),
            types.InlineKeyboardButton(text=KeyboardTitles.reject_task, callback_data=CallbackDataKeys.reject_detail),
        ],
        [types.InlineKeyboardButton(text=KeyboardTitles.end_detail, callback_data=CallbackDataKeys.end_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_queue, callback_data=CallbackDataKeys.back_to_queue)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_teacher_actions_two() -> types.InlineKeyboardMarkup:
    buttons = [
        [
            types.InlineKeyboardButton(text=KeyboardTitles.accept_detail_already_accepted,
                                       callback_data=CallbackDataKeys.accept_detail),
            types.InlineKeyboardButton(text=KeyboardTitles.reject_detail_already_accepted,
                                       callback_data=CallbackDataKeys.reject_detail),
        ],
        [types.InlineKeyboardButton(text=KeyboardTitles.end_detail_accepted, callback_data=CallbackDataKeys.end_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_queue, callback_data=CallbackDataKeys.back_to_queue)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_task_card_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.change_current_task,
                                    callback_data=CallbackDataKeys.change_current_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.first_task, callback_data=CallbackDataKeys.task_one),
         types.InlineKeyboardButton(text=KeyboardTitles.second_task, callback_data=CallbackDataKeys.task_two)],
        [types.InlineKeyboardButton(text=KeyboardTitles.add_tasks_to_student,
                                    callback_data=CallbackDataKeys.add_tasks_to_student)],
        [types.InlineKeyboardButton(text=KeyboardTitles.reject_current_task,
                                    callback_data=CallbackDataKeys.reject_current_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_tasks_teacher)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_penalty_card_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.add_penalty, callback_data=CallbackDataKeys.add_penalty),
         types.InlineKeyboardButton(text=KeyboardTitles.remove_penalty, callback_data=CallbackDataKeys.remove_penalty)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_penalties_teacher)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_back_to_main_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_main_teacher)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_back_to_details_teacher() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_details_teacher)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_student_card_actions() -> types.InlineKeyboardMarkup:
    buttons = [
        [
            types.InlineKeyboardButton(text="Добавить штраф⚖️", callback_data="setpenalty"),
            types.InlineKeyboardButton(text="Убрать штраф↩️", callback_data="removepenalty"),
        ],
        [types.InlineKeyboardButton(text="Назад⬅️", callback_data="back_to_list_of_students")],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_inventory() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.ADD_DETAIL, callback_data=CallbackDataKeys.INVENTORY_ADD)],
        [types.InlineKeyboardButton(text=KeyboardTitles.BACK, callback_data=CallbackDataKeys.BACK_TO_INVENTORY)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_alias_back() -> types.InlineKeyboardMarkup:
    buttons = [[types.InlineKeyboardButton(text=KeyboardTitles.BACK,
                                           callback_data=CallbackDataKeys.BACK_TO_INVENTORY)]]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_alias_back_student() -> types.InlineKeyboardMarkup:
    buttons = [[types.InlineKeyboardButton(text="⬅️ Назад",
                                           callback_data="back_to_inventory_student")]]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_transfer_return() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="🔄 Передать", callback_data=CallbackDataKeys.TRANSFER_ITEM)],
        [types.InlineKeyboardButton(text="↩️ Вернуть", callback_data=CallbackDataKeys.RETURN_ITEM)],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data=CallbackDataKeys.BACK_TO_INVENTORY)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_process_high_urgency_teacher() -> types.InlineKeyboardMarkup:
    """Keyboard for processing high urgency requests."""
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.confirm_high_urgency,
                                    callback_data=CallbackDataKeys.confirm_high_urgency)],
        [types.InlineKeyboardButton(text=KeyboardTitles.reject_high_urgency,
                                    callback_data=CallbackDataKeys.reject_high_urgency)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_task_card_teacher() -> types.InlineKeyboardMarkup:
    """Keyboard for task card management."""
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.change_current_task,
                                    callback_data=CallbackDataKeys.change_current_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.first_task, callback_data=CallbackDataKeys.task_one),
         types.InlineKeyboardButton(text=KeyboardTitles.second_task, callback_data=CallbackDataKeys.task_two)],
        [types.InlineKeyboardButton(text=KeyboardTitles.add_tasks_to_student,
                                    callback_data=CallbackDataKeys.add_tasks_to_student)],
        [types.InlineKeyboardButton(text=KeyboardTitles.reject_current_task,
                                    callback_data=CallbackDataKeys.reject_current_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_tasks_teacher)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_penalty_card_teacher() -> types.InlineKeyboardMarkup:
    """Keyboard for penalty management."""
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.add_penalty, callback_data=CallbackDataKeys.add_penalty),
         types.InlineKeyboardButton(text=KeyboardTitles.remove_penalty, callback_data=CallbackDataKeys.remove_penalty)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_penalties_teacher)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
