"""Shared keyboard utilities and callback data keys."""

from aiogram import types
from aiogram.utils.keyboard import KeyboardBuilder, ReplyKeyboardBuilder
from src.modules.shared.messages import KeyboardTitles


class CallbackDataKeys:
    """Centralized callback data constants."""
    # Callback data for registration
    start_registration_client = "student"
    start_registration_operator = "teacher"

    # Callback data for student actions
    upload_detail = "send_piece"
    details_queue = "student_requests"
    tasks = "tasks"

    submit_tasks = "submit_tasks"
    close_tasks = "close_tasks"

    end_current_task = "end_current_task"
    continue_current_task = "continue_current_task"

    # Callback data for urgency levels
    urgency_high = "high"
    urgency_medium = "medium"
    urgency_low = "low"

    details_queue_teacher = "details_queue_teacher"
    client_tasks = "client_tasks"
    clients = "clients"

    # Callback data for teacher actions
    open_queue = "check"
    history = "history"
    xlsx = "xlsx"

    sort_by_type = "sort_type"
    sort_by_date = "sort_date"
    sort_by_urgency = "sort_urgency"
    back_to_main_teacher = "back_to_main_teacher"
    back_to_details_teacher = "back_to_details_teacher"
    back_to_main_teacher_no_edit = "back_to_main_teacher_no_edit"
    back_to_tasks_teacher = "back_to_tasks_teacher"
    back_to_penalties_teacher = "back_to_penalties_teacher"

    # Callback data for teacher process actions
    confirm_high_urgency = "accept_high_urgency"
    reject_high_urgency = "reject_high_urgency"
    accept_detail = "accept"
    reject_detail = "reject"

    accept_task = "accept_task"
    reject_task = "reject_task"

    accept_end_of_session = "accept_end_of_session"
    reject_end_of_session = "reject_end_of_session"

    end_task = "end"
    back_to_queue = "back_to_queue"

    # Back to main menu for student
    back_to_main_student = "back_to_main_student"

    add_10_minutes = "10"
    add_15_minutes = "15"
    add_30_minutes = "30"

    change_current_task = "change_current_task"
    reject_current_task = "reject_current_task"

    task_one = "task_one"
    task_two = "task_two"

    penalties = "penalty"
    add_penalty = "add_penalty"
    remove_penalty = "remove_penalty"
    add_tasks_to_student = "add_tasks_to_student"

    # Equipment and inventory
    INVENTORY_ADD = "inventory_add"
    BACK_TO_INVENTORY = "back_to_inventory"
    TRANSFER_ITEM = "transfer_item"
    RETURN_ITEM = "return_item"
    STUDENT_EQUIPMENT = "student_equipment"


# Общие утилиты для клавиатур могут остаться здесь
    reject_task = "reject_task"

    accept_end_of_session = "accept_end_of_session"
    reject_end_of_session = "reject_end_of_session"

    end_task = "end"
    back_to_queue = "back_to_queue"

    # Back to main menu for student
    back_to_main_student = "back_to_main_student"

    add_10_minutes = "10"
    add_15_minutes = "15"
    add_30_minutes = "30"

    change_current_task = "change_current_task"
    reject_current_task = "reject_current_task"

    task_one = "task_one"
    task_two = "task_two"

    penalties = "penalty"
    add_penalty = "add_penalty"
    remove_penalty = "remove_penalty"
    add_tasks_to_student = "add_tasks_to_student"

    # BACK_TO_MAIN = "back_to_main"
    INVENTORY_ADD = "inventory_add"
    BACK_TO_INVENTORY = "back_to_inventory"
    TRANSFER_ITEM = "transfer_item"
    RETURN_ITEM = "return_item"
    STUDENT_EQUIPMENT = "student_equipment"


def keyboard_start_registration():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.start_registration_client,
                                    callback_data=CallbackDataKeys.start_registration_client)],
        [types.InlineKeyboardButton(text=KeyboardTitles.start_registration_operator,
                                    callback_data=CallbackDataKeys.start_registration_operator)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


# TODO: change callback data and put into vars
def keyboard_student_card_actions():
    buttons = [
        # [types.InlineKeyboardButton(text="Задание 1️⃣", callback_data="t1"),
        #  types.InlineKeyboardButton(text="Задание 2️⃣", callback_data="t2")],
        # [types.InlineKeyboardButton(text="Установить задания 🔢", callback_data="settask"),
        #  types.InlineKeyboardButton(text="Отклонить задания🙅‍♂️", callback_data="removetask")],
        [types.InlineKeyboardButton(text="Добавить штраф⚖️", callback_data="setpenalty"),
         types.InlineKeyboardButton(text="Убрать штраф↩️", callback_data="removepenalty")],
        [types.InlineKeyboardButton(text="Назад⬅️", callback_data="back_to_list_of_students")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_main_student():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.upload_detail, callback_data=CallbackDataKeys.upload_detail)],
        [types.InlineKeyboardButton(text=KeyboardTitles.task_queue, callback_data=CallbackDataKeys.details_queue)],
        [types.InlineKeyboardButton(text=KeyboardTitles.tasks, callback_data=CallbackDataKeys.tasks)],
        [types.InlineKeyboardButton(text="📦Комплектующие", callback_data="student_equipment")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_submit_tasks_student():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.submit_tasks, callback_data=CallbackDataKeys.submit_tasks)],
        [types.InlineKeyboardButton(text=KeyboardTitles.close_tasks, callback_data=CallbackDataKeys.close_tasks)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_student,
                                    callback_data=CallbackDataKeys.back_to_main_student)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_end_of_hour_check_student():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.end_current_task,
                                    callback_data=CallbackDataKeys.end_current_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.continue_current_task,
                                    callback_data=CallbackDataKeys.continue_current_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.add_10_minutes,
                                    callback_data=CallbackDataKeys.add_10_minutes),
         types.InlineKeyboardButton(text=KeyboardTitles.add_15_minutes,
                                    callback_data=CallbackDataKeys.add_15_minutes),
         types.InlineKeyboardButton(text=KeyboardTitles.add_30_minutes,
                                    callback_data=CallbackDataKeys.add_30_minutes),
         ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_urgency_student():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.urgency_high, callback_data=CallbackDataKeys.urgency_high)],
        [types.InlineKeyboardButton(text=KeyboardTitles.urgency_medium, callback_data=CallbackDataKeys.urgency_medium)],
        [types.InlineKeyboardButton(text=KeyboardTitles.urgency_low, callback_data=CallbackDataKeys.urgency_low)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_student,
                                    callback_data=CallbackDataKeys.back_to_main_student)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_back_to_main_student():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_student,
                                    callback_data=CallbackDataKeys.back_to_main_student)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_process_end_of_session_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.confirm_high_urgency,
                                    callback_data=CallbackDataKeys.accept_end_of_session)],
        [types.InlineKeyboardButton(text=KeyboardTitles.reject_high_urgency,
                                    callback_data=CallbackDataKeys.reject_end_of_session)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_main_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.details_queue_teacher,
                                    callback_data=CallbackDataKeys.details_queue_teacher)],
        [types.InlineKeyboardButton(text="👦🏻Клиенты",
                                    callback_data="clients")],
        # [types.InlineKeyboardButton(text=KeyboardTitles.client_tasks,
        #                             callback_data=CallbackDataKeys.client_tasks)],
        # [types.InlineKeyboardButton(text=KeyboardTitles.penalties,
        #                             callback_data=CallbackDataKeys.penalties)],
        [types.InlineKeyboardButton(text="📦Комплектующие", callback_data="teacher_equipment")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_details_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.open_queue, callback_data=CallbackDataKeys.open_queue)],
        [types.InlineKeyboardButton(text=KeyboardTitles.history, callback_data=CallbackDataKeys.history)],
        [types.InlineKeyboardButton(text=KeyboardTitles.get_xlsx, callback_data=CallbackDataKeys.xlsx)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_queue,
                                    callback_data=CallbackDataKeys.back_to_main_teacher)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_sort_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.sort_by_type, callback_data=CallbackDataKeys.sort_by_type)],
        [types.InlineKeyboardButton(text=KeyboardTitles.sort_by_date, callback_data=CallbackDataKeys.sort_by_date)],
        [types.InlineKeyboardButton(text=KeyboardTitles.sort_by_urgency,
                                    callback_data=CallbackDataKeys.sort_by_urgency)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_details_teacher)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_teacher_actions_one():
    # builder = ReplyKeyboardBuilder()
    buttons = [
        [
            types.InlineKeyboardButton(text=KeyboardTitles.accept_task, callback_data=CallbackDataKeys.accept_detail),
            types.InlineKeyboardButton(text=KeyboardTitles.reject_task, callback_data=CallbackDataKeys.reject_detail)
        ],
        [types.InlineKeyboardButton(text=KeyboardTitles.end_detail, callback_data=CallbackDataKeys.end_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_queue, callback_data=CallbackDataKeys.back_to_queue)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_teacher_actions_two():
    # builder = ReplyKeyboardBuilder()
    buttons = [
        [
            types.InlineKeyboardButton(text=KeyboardTitles.accept_detail_already_accepted,
                                       callback_data=CallbackDataKeys.accept_detail),
            types.InlineKeyboardButton(text=KeyboardTitles.reject_detail_already_accepted,
                                       callback_data=CallbackDataKeys.reject_detail)
        ],
        [types.InlineKeyboardButton(text=KeyboardTitles.end_detail_accepted, callback_data=CallbackDataKeys.end_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_queue, callback_data=CallbackDataKeys.back_to_queue)]
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


def keyboard_process_submit_task_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.confirm_high_urgency,
                                    callback_data=CallbackDataKeys.accept_task)],
        [types.InlineKeyboardButton(text=KeyboardTitles.reject_high_urgency,
                                    callback_data=CallbackDataKeys.reject_task)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_task_card_teacher():
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


def keyboard_penalty_card_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.add_penalty, callback_data=CallbackDataKeys.add_penalty),
         types.InlineKeyboardButton(text=KeyboardTitles.remove_penalty, callback_data=CallbackDataKeys.remove_penalty)],
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_penalties_teacher)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_back_to_main_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_main_teacher)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_back_to_details_teacher():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.back_to_main_teacher,
                                    callback_data=CallbackDataKeys.back_to_details_teacher)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_inventory():
    buttons = [
        [types.InlineKeyboardButton(text=KeyboardTitles.ADD_DETAIL, callback_data=CallbackDataKeys.INVENTORY_ADD)],
        [types.InlineKeyboardButton(text=KeyboardTitles.BACK, callback_data="back_to_inventory")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_alias_back():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=KeyboardTitles.BACK, callback_data=CallbackDataKeys.BACK_TO_INVENTORY)]]
    )

# def keyboard_inventory():
#     buttons = [
#         [types.InlineKeyboardButton(text="➕ Добавить", callback_data="inventory_add")],
#         # [types.InlineKeyboardButton(text="🛒 Корзина", callback_data="inventory_bucket")],
#         [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
#     ]
#     return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_alias_back():
    buttons = [
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_inventory")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def keyboard_alias_back_student():
    buttons = [
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_inventory_student")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def keyboard_transfer_return():
    buttons = [
        [types.InlineKeyboardButton(text="🔄 Передать", callback_data="transfer_item")],
        [types.InlineKeyboardButton(text="↩️ Вернуть", callback_data="return_item")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_inventory")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
