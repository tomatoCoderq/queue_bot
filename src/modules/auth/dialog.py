"""Auth dialog registration and setup."""

from aiogram_dialog import Dialog

from src.modules.auth.states import AuthSG
from src.modules.auth.windows import (
    choose_role_window,
    student_name_input_window,
    teacher_confirm_window,
    student_menu_window,
    teacher_menu_window,
)


# Create the auth dialog with all windows
auth_dialog = Dialog(
    choose_role_window,
    student_name_input_window,
    teacher_confirm_window,
    student_menu_window,
    teacher_menu_window,
)
