"""States for tasks module using aiogram_dialog."""

from aiogram.fsm.state import State, StatesGroup


class TasksSG(StatesGroup):
    """States group for tasks management."""
    
    # Viewing tasks
    view_tasks = State()
    
    # Submitting new tasks
    submit_task_first = State()
    submit_task_second = State()
    
    # Closing current tasks
    close_tasks_confirm = State()
    
    # Ending current task and adding new one
    end_current_task = State()
    add_new_second_task = State()
    
    # Continue current task with time extension
    continue_task_options = State()
