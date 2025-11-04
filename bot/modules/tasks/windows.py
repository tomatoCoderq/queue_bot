from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Back, Row
from bot.modules.start.windows import StudentStates, OperatorStates


def create_task_dialogs():
    """
    Create dialogs for tasks functionality.
    Separate dialogs for Student and Operator roles.
    """
    # Import handlers here to avoid circular imports
    from bot.modules.tasks.handlers import (
        get_student_tasks_data,
        get_task_detail_data,
        on_task_select,
        on_back_to_profile,
        get_operator_students_data,
        on_student_select,
        get_student_tasks_for_operator_data,
        on_page_next,
        on_page_prev,
    )
    
    # ============ STUDENT WINDOWS ============
    
    # Window 1: Student's tasks list
    student_tasks_window = Window(
        Format(
            "📚 Мои задачи\n\n"
            "Всего задач: {tasks_count}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("{item[title]} ({item[status_emoji]})"),
                id="task_select",
                item_id_getter=lambda x: x["id"],
                items="tasks",
                on_click=on_task_select,
            ),
            id="tasks_scroll",
            width=1,
            height=10,
        ),
        Button(
            Const("🔙 В профиль"),
            id="back_to_profile",
            on_click=on_back_to_profile,
        ),
        getter=get_student_tasks_data,
        state=StudentStates.MY_TASKS,
    )
    
    # Window 2: Task detail for student
    student_task_detail_window = Window(
        Format(
            "📋 Детали задачи\n\n"
            "📌 Название: {task[title]}\n"
            "📝 Описание: {task[description]}\n"
            "📅 Дата начала: {task[start_date]}\n"
            "⏰ Дедлайн: {task[due_date]}\n"
            "🎯 Статус: {task[status_display]}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        Back(Const("🔙 К списку задач")),
        getter=get_task_detail_data,
        state=StudentStates.TASK_DETAIL,
    )
    
    # ============ OPERATOR WINDOWS ============
    
    # Window 1: List of students with pagination
    operator_students_window = Window(
        Format(
            "👥 Список студентов\n\n"
            "Всего студентов: {total_students}\n"
            "Страница {current_page} из {total_pages}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("{item[first_name]} {item[last_name]}"),
                id="student_select",
                item_id_getter=lambda x: str(x["telegram_id"]),
                items="students_page",
                on_click=on_student_select,
            ),
            id="students_scroll",
            width=1,
            height=5,  # Max 5 students per page
        ),
        Row(
            Button(
                Const("◀️ Назад"),
                id="page_prev",
                on_click=on_page_prev,
                when="has_prev",
            ),
            Button(
                Const("Вперёд ▶️"),
                id="page_next",
                on_click=on_page_next,
                when="has_next",
            ),
        ),
        Button(
            Const("🔙 В профиль"),
            id="back_to_profile",
            on_click=on_back_to_profile,
        ),
        getter=get_operator_students_data,
        state=OperatorStates.STUDENTS_LIST,
    )
    
    # Window 2: Student's tasks (viewed by operator)
    operator_student_tasks_window = Window(
        Format(
            "📚 Задачи студента: {student_name}\n\n"
            "Всего задач: {tasks_count}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("{item[title]} ({item[status_emoji]})"),
                id="task_select_operator",
                item_id_getter=lambda x: x["id"],
                items="tasks",
                on_click=on_task_select,
            ),
            id="tasks_scroll_operator",
            width=1,
            height=10,
        ),
        Back(Const("🔙 К списку студентов")),
        getter=get_student_tasks_for_operator_data,
        state=OperatorStates.STUDENT_TASKS,
    )
    
    # Window 3: Task detail (viewed by operator)
    operator_task_detail_window = Window(
        Format(
            "📋 Детали задачи\n\n"
            "👤 Студент: {student_name}\n"
            "📌 Название: {task[title]}\n"
            "📝 Описание: {task[description]}\n"
            "📅 Дата начала: {task[start_date]}\n"
            "⏰ Дедлайн: {task[due_date]}\n"
            "🎯 Статус: {task[status_display]}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        Back(Const("🔙 К задачам студента")),
        getter=get_task_detail_data,
        state=OperatorStates.TASK_DETAIL,
    )
    
    # Create dialogs
    student_tasks_dialog = Dialog(
        student_tasks_window,
        student_task_detail_window,
    )
    
    operator_tasks_dialog = Dialog(
        operator_students_window,
        operator_student_tasks_window,
        operator_task_detail_window,
    )
    
    return student_tasks_dialog, operator_tasks_dialog
