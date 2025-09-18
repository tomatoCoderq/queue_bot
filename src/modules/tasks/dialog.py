"""Tasks dialog registration and setup."""

from aiogram_dialog import Dialog

from src.modules.tasks.windows import (
    view_tasks_window,
    submit_first_task_window,
    submit_second_task_window,
    close_tasks_window,
    end_task_window,
    continue_task_window,
)


# Create the tasks dialog with all windows
tasks_dialog = Dialog(
    view_tasks_window,
    submit_first_task_window,
    submit_second_task_window,
    close_tasks_window,
    end_task_window,
    continue_task_window,
)
