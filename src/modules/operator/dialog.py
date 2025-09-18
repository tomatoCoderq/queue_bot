"""Operator tasks dialog registration and setup."""

from aiogram_dialog import Dialog

from src.modules.operator.windows import (
    tasks_main_menu_window,
    client_selection_window,
    client_task_card_window,
    change_task_one_window,
    change_task_two_window,
)


# Create the operator tasks dialog with all windows
operator_tasks_dialog = Dialog(
    tasks_main_menu_window,
    client_selection_window,
    client_task_card_window,
    change_task_one_window,
    change_task_two_window,
)
