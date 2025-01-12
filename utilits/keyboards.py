from aiogram import types


def keyboard_start_registration():
    buttons = [[types.InlineKeyboardButton(text="Ученик", callback_data="student")],
               [types.InlineKeyboardButton(text="Преподаватель", callback_data="teacher")]]
    # [types.InlineKeyboardButton(text="Родитель", callback_data="parent")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def keyboard_main_student():
    buttons = [[types.InlineKeyboardButton(text="Отослать на печать/резку", callback_data="send_piece")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def keyboard_urgency_student():
    buttons = [[types.InlineKeyboardButton(text="Высокая", callback_data="high")],
               [types.InlineKeyboardButton(text="Средняя", callback_data="medium")],
               [types.InlineKeyboardButton(text="Низкая", callback_data="low")],
               [types.InlineKeyboardButton(text="Назад", callback_data="back_to_main_student")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def keyboard_main_teacher():
    buttons = [[types.InlineKeyboardButton(text="Открыть очередь", callback_data="check")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def keyboard_sort_teacher():
    buttons = [[types.InlineKeyboardButton(text="Сортировка по типу", callback_data="sort_type")],
               [types.InlineKeyboardButton(text="Сортировка по дате", callback_data="sort_date")],
               [types.InlineKeyboardButton(text="Сортировка по срочности", callback_data="sort_urgency")],
               [types.InlineKeyboardButton(text="Назад", callback_data="back_to_main_teacher")], ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def keyboard_teacher_actions():
    buttons = [[types.InlineKeyboardButton(text="Принять на печать/резку", callback_data="accept")],
               [types.InlineKeyboardButton(text="Закончить печать/резку", callback_data="end")],
               [types.InlineKeyboardButton(text="Назад", callback_data="back_to_queue")], ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
