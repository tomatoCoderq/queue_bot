from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Back, Row
from aiogram_dialog.widgets.input import TextInput
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
        # Task creation handlers
        on_create_task_start,
        on_task_title_input,
        on_task_description_input,
        on_task_start_date_input,
        on_task_due_date_input,
        on_no_due_date,
        on_confirm_create_task,
        on_cancel_create_task,
        # Quick due date handlers
        on_due_date_30min,
        on_due_date_45min,
        on_due_date_1hour,
        on_due_date_2hours,
        on_due_date_4hours,
        on_due_date_8hours,
        on_due_date_1day,
        # Getter for confirmation window
        get_create_task_confirm_data,
        # Sort handlers
        on_sort_by_start_date,
        on_sort_by_due_date,
        on_sort_by_status,
        on_sort_reset,
    )
    
    # ============ STUDENT WINDOWS ============
    
    # Window 1: Student's tasks list
    student_tasks_window = Window(
        Format(
            "📚 Мои задачи\n\n"
            "Всего задач: {tasks_count}\n"
            "Сортировка: {sort_display}\n"
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
            height=5,
        ),
        Row(
            Button(
                Const("📅 Начало"),
                id="sort_start",
                on_click=on_sort_by_start_date,
            ),
            Button(
                Const("⏰ Дедлайн"),
                id="sort_due",
                on_click=on_sort_by_due_date,
            ),
        ),
        Row(
            Button(
                Const("🎯 Статус"),
                id="sort_status",
                on_click=on_sort_by_status,
            ),
            Button(
                Const("🔄 Сброс"),
                id="sort_reset",
                on_click=on_sort_reset,
            ),
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
            "Сортировка: {sort_display}\n"
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
            height=5,
        ),
        Row(
            Button(
                Const("📅 Начало"),
                id="sort_start_op",
                on_click=on_sort_by_start_date,
            ),
            Button(
                Const("⏰ Дедлайн"),
                id="sort_due_op",
                on_click=on_sort_by_due_date,
            ),
        ),
        Row(
            Button(
                Const("🎯 Статус"),
                id="sort_status_op",
                on_click=on_sort_by_status,
            ),
            Button(
                Const("🔄 Сброс"),
                id="sort_reset_op",
                on_click=on_sort_reset,
            ),
        ),
        Button(
            Const("➕ Создать задачу"),
            id="create_task_btn",
            on_click=on_create_task_start,
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
    
    # ============ TASK CREATION WINDOWS (FOR OPERATOR) ============
    
    # Window 1: Enter task title
    create_task_title_window = Window(
        Const("➕ Создание задачи\n\n"
              "Шаг 1 из 4: Введите название задачи"),
        TextInput(
            id="task_title_input",
            type_factory=str,
            on_success=on_task_title_input,
        ),
        Back(Const("❌ Отменить")),
        state=OperatorStates.CREATE_TASK_TITLE,
    )
    
    # Window 2: Enter task description
    create_task_description_window = Window(
        Format(
            "➕ Создание задачи\n\n"
            "Шаг 2 из 4: Введите описание задачи\n\n"
            "📌 Название: {dialog_data[task_title]}"
        ),
        TextInput(
            id="task_description_input",
            type_factory=str,
            on_success=on_task_description_input,
        ),
        Back(Const("🔙 Назад")),
        state=OperatorStates.CREATE_TASK_DESCRIPTION,
    )
    
    # Window 3: Enter start date
    create_task_start_date_window = Window(
        Format(
            "➕ Создание задачи\n\n"
            "Шаг 3 из 4: Введите дату и время начала\n\n"
            "📌 Название: {dialog_data[task_title]}\n"
            "📝 Описание: {dialog_data[task_description]}\n\n"
            "Формат: YYYY-MM-DD HH:MM\n"
            "Например: 2025-11-05 14:30\n\n"
            "Можно указать только дату: 2025-11-05"
        ),
        TextInput(
            id="task_start_date_input",
            type_factory=str,
            on_success=on_task_start_date_input,
        ),
        Back(Const("🔙 Назад")),
        state=OperatorStates.CREATE_TASK_START_DATE,
    )
    
    # Window 4: Enter due date
    create_task_due_date_window = Window(
        Format(
            "➕ Создание задачи\n\n"
            "Шаг 4 из 4: Установите дедлайн\n\n"
            "📌 Название: {dialog_data[task_title]}\n"
            "📝 Описание: {dialog_data[task_description]}\n"
            "📅 Дата начала: {dialog_data[task_start_date]}\n\n"
            "Выберите быстрый вариант или введите вручную:"
        ),
        # Quick deadline buttons (2 rows)
        Row(
            Button(
                Const("⏱ 30 мин"),
                id="due_30min",
                on_click=on_due_date_30min,
            ),
            Button(
                Const("⏱ 45 мин"),
                id="due_45min",
                on_click=on_due_date_45min,
            ),
            Button(
                Const("⏱ 1 час"),
                id="due_1hour",
                on_click=on_due_date_1hour,
            ),
        ),
        Row(
            Button(
                Const("⏱ 2 часа"),
                id="due_2hours",
                on_click=on_due_date_2hours,
            ),
            Button(
                Const("⏱ 4 часа"),
                id="due_4hours",
                on_click=on_due_date_4hours,
            ),
        ),
        Row(
            Button(
                Const("⏱ 8 часов"),
                id="due_8hours",
                on_click=on_due_date_8hours,
            ),
            Button(
                Const("📅 1 день"),
                id="due_1day",
                on_click=on_due_date_1day,
            ),
        ),
        # Manual input
        TextInput(
            id="task_due_date_input",
            type_factory=str,
            on_success=on_task_due_date_input,
        ),
        # No deadline button
        Button(
            Const("🚫 Без дедлайна"),
            id="no_due_date",
            on_click=on_no_due_date,
        ),
        Back(Const("🔙 Назад")),
        state=OperatorStates.CREATE_TASK_DUE_DATE,
    )
    
    # Window 5: Confirm task creation
    create_task_confirm_window = Window(
        Format(
            "✅ Подтвердите создание задачи\n\n"
            "👤 Студент: {student_name}\n\n"
            "📌 Название: {dialog_data[task_title]}\n"
            "📝 Описание: {dialog_data[task_description]}\n"
            "📅 Дата начала: {dialog_data[task_start_date]}\n"
            "⏰ Дедлайн: {dialog_data[task_due_date]}\n\n"
            "Создать задачу и назначить студенту?"
        ),
        Row(
            Button(
                Const("✅ Создать"),
                id="confirm_create_task",
                on_click=on_confirm_create_task,
            ),
            Button(
                Const("❌ Отменить"),
                id="cancel_create_task",
                on_click=on_cancel_create_task,
            ),
        ),
        getter=get_create_task_confirm_data,
        state=OperatorStates.CREATE_TASK_CONFIRM,
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
        # Task creation windows
        create_task_title_window,
        create_task_description_window,
        create_task_start_date_window,
        create_task_due_date_window,
        create_task_confirm_window,
    )
    
    return student_tasks_dialog, operator_tasks_dialog
