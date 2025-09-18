"""States for operator tasks module using aiogram_dialog."""

from aiogram.fsm.state import State, StatesGroup


class OperatorTasksSG(StatesGroup):
    """States group for operator tasks management."""
    
    # Main menu for tasks management
    tasks_main_menu = State()
    
    # Client selection and task viewing
    client_selection = State()
    client_task_card = State()
    
    # Task modification
    change_task_one = State()
    change_task_two = State()
    
    # Processing submitted tasks
    process_task_submit = State()
    
    # Processing end of session
    process_end_session = State()
    
    # History and reports
    tasks_history = State()
    generate_report = State()
