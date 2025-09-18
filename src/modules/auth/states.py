"""States for auth module using aiogram_dialog."""

from aiogram.fsm.state import StatesGroup, State


class AuthSG(StatesGroup):
    """Auth states group."""
    
    # Main auth states
    choose_role = State()
    
    # Student registration
    student_name_input = State()
    
    # Teacher registration
    teacher_confirm = State()
    
    # Already registered users
    main_menu_student = State()
    main_menu_teacher = State()
