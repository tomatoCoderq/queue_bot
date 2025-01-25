from aiogram import types
from aiogram.utils.keyboard import KeyboardBuilder, ReplyKeyboardBuilder
from app.utilits.messages import KeyboardTitles


class CallbackDataKeys:
    # Callback data for registration
    start_registration_client = "student"
    start_registration_operator = "teacher"

    # Callback data for student actions
    upload_task = "send_piece"
    task_queue = "student_requests"

    # Callback data for urgency levels
    urgency_high = "high"
    urgency_medium = "medium"
    urgency_low = "low"

    # Callback data for teacher actions
    open_queue = "check"
    sort_by_type = "sort_type"
    sort_by_date = "sort_date"
    sort_by_urgency = "sort_urgency"
    back_to_main_teacher = "back_to_main_teacher"

    # Callback data for teacher process actions
    confirm_high_urgency = "accept_high_urgency"
    reject_high_urgency = "reject_high_urgency"
    accept_task = "accept"
    reject_task = "reject"
    end_task = "end"
    back_to_queue = "back_to_queue"

    # Back to main menu for student
    back_to_main_student = "back_to_main_student"


def keyboard_start_registration():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.start_registration_client,
                                    callback_data=CallbackDataKeys.start_registration_client)],
        [types.InlineKeyboardButton(text=KeyboardTitles.start_registration_operator,
                                    callback_data=CallbackDataKeys.start_registration_operator)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_main_student():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.upload_task, callback_data=CallbackDataKeys.upload_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.task_queue, callback_data=CallbackDataKeys.task_queue)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_process_high_urgency_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.confirm_high_urgency,
                                    callback_data=CallbackDataKeys.confirm_high_urgency)],
        [types.InlineKeyboardButton(text=KeyboardTitles.reject_high_urgency,
                                    callback_data=CallbackDataKeys.reject_high_urgency)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_urgency_student():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.urgency_high, callback_data=CallbackDataKeys.urgency_high)],
        [types.InlineKeyboardButton(text=KeyboardTitles.urgency_medium, callback_data=CallbackDataKeys.urgency_medium)],
        [types.InlineKeyboardButton(text=KeyboardTitles.urgency_low, callback_data=CallbackDataKeys.urgency_low)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_main_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.open_queue, callback_data=CallbackDataKeys.open_queue)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_sort_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.sort_by_type, callback_data=CallbackDataKeys.sort_by_type)],
        [types.InlineKeyboardButton(text=KeyboardTitles.sort_by_date, callback_data=CallbackDataKeys.sort_by_date)],
        [types.InlineKeyboardButton(text=KeyboardTitles.sort_by_urgency,
                                    callback_data=CallbackDataKeys.sort_by_urgency)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_main_teacher)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_teacher_actions_one():
    # builder = ReplyKeyboardBuilder()
    buttons = [
        [
            types.InlineKeyboardButton(text=KeyboardTitles.accept_task, callback_data=CallbackDataKeys.accept_task),
            types.InlineKeyboardButton(text=KeyboardTitles.reject_task, callback_data=CallbackDataKeys.reject_task)
        ],
        [types.InlineKeyboardButton(text=KeyboardTitles.end_task, callback_data=CallbackDataKeys.end_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_queue, callback_data=CallbackDataKeys.back_to_queue)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_teacher_actions_two():
    # builder = ReplyKeyboardBuilder()
    buttons = [
        [
            types.InlineKeyboardButton(text=KeyboardTitles.accept_task_already_accepted, callback_data=CallbackDataKeys.accept_task),
            types.InlineKeyboardButton(text=KeyboardTitles.reject_task_already_accepted, callback_data=CallbackDataKeys.reject_task)
        ],
        [types.InlineKeyboardButton(text=KeyboardTitles.end_task_accepted, callback_data=CallbackDataKeys.end_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_queue, callback_data=CallbackDataKeys.back_to_queue)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)



def keyboard_back_to_main_student():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_student,
                                    callback_data=CallbackDataKeys.back_to_main_student)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
