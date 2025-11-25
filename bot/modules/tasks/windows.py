from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Back, Row, Cancel
from aiogram_dialog.widgets.input import TextInput
from bot.modules.states import (
    StudentStates,
    OperatorStudentsStates,
    OperatorTaskCreateStates,
    OperatorReviewStates,
    OperatorTaskStates,
)



def create_task_dialogs():
    """
    Create dialogs for tasks functionality.
    Separate dialogs for Student and Operator roles.
    """
    # Import handlers here to avoid circular imports
    from bot.modules.tasks.handlers import (

        on_task_select,
        on_back_to_profile,
        get_operator_students_data,
        on_student_select,
        # get_student_tasks_for_operator_data,
        on_page_next,
        tasks_list_getter,
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
        # Sort handlers
        on_sort_by_start_date,
        on_sort_by_due_date,
        on_sort_by_status,
        on_sort_reset,
        on_toggle_completed_tasks,
        # Submit/Review handlers
        on_submit_task_button,
        on_task_result_input,
        get_submitted_tasks_data,
        on_submitted_task_select,
        get_review_task_detail_data,
        on_approve_task,
        on_reject_task_button,
        on_rejection_comment_input,
        task_detail_getter
    )

    # ============ STUDENT WINDOWS ============

    # Window 1: Student's tasks list
    student_tasks_window = Window(
        Format(
            "📚 Мои задачи\n\n"
            "Показано задач: {tasks_count}\n"
            "Выполнено: {completed_count} из {total_count}\n"
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
            Format("{toggle_button_text}"),
            id="toggle_completed",
            on_click=on_toggle_completed_tasks,
        ),
        Button(
            Const("🔙 В профиль"),
            id="back_to_profile",
            on_click=on_back_to_profile,
        ),
        getter=tasks_list_getter,
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
            "━━━━━━━━━━━━━━━━━━━━━━\n",
        ),
        Format(
            "❌ Комментарий преподавателя:\n{task[rejection_comment]}\n\n",
            when="task[has_rejection]"
        ),
        Format(
            "{overdue_warning}\n",
            when="is_overdue"
        ),
        Button(
            Const("✅ Завершить задание"),
            id="submit_task",
            on_click=on_submit_task_button,
            # when="can_submit",
        ),
        Back(Const("🔙 К списку задач")),
        getter=task_detail_getter,
        state=StudentStates.TASK_DETAIL,
    )

    # Window 3: Submit task result
    student_submit_result_window = Window(
        Const(
            "📝 Отправка результата\n\n"
            "Введите результат выполнения задания.\n"
            "Он будет отправлен преподавателю на проверку."
        ),
        TextInput(
            id="result_input",
            on_success=on_task_result_input,
        ),
        Back(Const("🔙 Отмена")),
        state=StudentStates.SUBMIT_TASK_RESULT,
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
        Button(
            Const("🔙 В профиль"),
            id="back_to_profile",
            on_click=on_back_to_profile,
        ),
        getter=get_operator_students_data,
        state=OperatorStudentsStates.STUDENTS_LIST,
    )
    # ============ TASK CREATION WINDOWS (FOR OPERATOR) ============

    create_task_title_window = Window(
        Const("➕ Создание задачи\n\n"
              "Шаг 1 из 4: Введите название задачи"),
        TextInput(
            id="task_title_input",
            type_factory=str,
            on_success=on_task_title_input,
        ),
        Cancel(Const("❌ Отменить")),
        state=OperatorTaskCreateStates.CREATE_TASK_TITLE,
    )

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
        state=OperatorTaskCreateStates.CREATE_TASK_DESCRIPTION,
    )

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
        state=OperatorTaskCreateStates.CREATE_TASK_START_DATE,
    )

    create_task_due_date_window = Window(
        Format(
            "➕ Создание задачи\n\n"
            "Шаг 4 из 4: Установите дедлайн\n\n"
            "📌 Название: {dialog_data[task_title]}\n"
            "📝 Описание: {dialog_data[task_description]}\n"
            "📅 Дата начала: {dialog_data[task_start_date]}\n\n"
            "Выберите быстрый вариант или введите вручную:"
        ),
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
        TextInput(
            id="task_due_date_input",
            type_factory=str,
            on_success=on_task_due_date_input,
        ),
        Button(
            Const("🚫 Без дедлайна"),
            id="no_due_date",
            on_click=on_no_due_date,
        ),
        Back(Const("🔙 Назад")),
        state=OperatorTaskCreateStates.CREATE_TASK_DUE_DATE,
    )

    create_task_confirm_window = Window(
        Format(
            "✅ Подтвердите создание задачи\n\n"
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
        state=OperatorTaskCreateStates.CREATE_TASK_CONFIRM,
    )

    # ============ OPERATOR REVIEW WINDOWS ============

    operator_submitted_tasks_window = Window(
        Format(
            "📝 Задачи на проверке\n\n"
            "Всего задач: {tasks_count}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("{item[title]} ({item[status_emoji]})"),
                id="submitted_task_select",
                item_id_getter=lambda x: x.get("index", "0"),
                items="tasks",
                on_click=on_submitted_task_select,
            ),
            id="submitted_tasks_scroll",
            width=1,
            height=5,
        ),
        Button(
            Const("🔙 В профиль"),
            id="back_to_profile",
            on_click=on_back_to_profile,
        ),
        getter=get_submitted_tasks_data,
        state=OperatorReviewStates.SUBMITTED_TASKS,
    )

    operator_review_task_window = Window(
        Format(
            "📋 Проверка задачи\n\n"
            "👤 Студент: {student_name}\n\n"
            "📌 Название: {task[title]}\n"
            "📝 Описание: {task[description]}\n"
            "📅 Дата начала: {task[start_date]}\n"
            "⏰ Дедлайн: {task[due_date]}\n\n"
            "✏️ Результат студента:\n{task[result]}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        Row(
            Button(
                Const("✅ Одобрить"),
                id="approve_task",
                on_click=on_approve_task,
            ),
            Button(
                Const("❌ Отклонить"),
                id="reject_task",
                on_click=on_reject_task_button,
            ),
        ),
        Back(Const("🔙 К списку")),
        getter=get_review_task_detail_data,
        state=OperatorReviewStates.REVIEW_TASK_DETAIL,
    )

    operator_rejection_comment_window = Window(
        Const(
            "💬 Комментарий к отклонению\n\n"
            "Напишите комментарий для студента,\n"
            "объясняя почему задание нужно переделать."
        ),
        TextInput(
            id="rejection_comment_input",
            on_success=on_rejection_comment_input,
        ),
        Back(Const("🔙 Отмена")),
        state=OperatorReviewStates.REJECT_TASK_COMMENT,
    )

    tasks_list_window = Window(
        Format(
            "📌 {header}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("{item[title]}"),
                id="unified_task_select",
                item_id_getter=lambda x: x["id"],
                items="tasks",
                on_click=on_task_select,
            ),
            id="unified_tasks_scroll",
            width=1,
            height=7,
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
        Cancel(Const("🔙 К списку студентов")),
        state=OperatorTaskStates.LIST_TASKS,
        getter=tasks_list_getter,
    )
    tasks_detail_window = Window(
        Format(
            "📋 Детали задачи\n\n"
            "📌 Название: {task[title]}\n"
            "📝 Описание: {task[description]}\n"
            "📅 Дата начала: {task[start_date]}\n"
            "⏰ Дедлайн: {task[due_date]}\n"
            "🎯 Статус: {task[status_display]}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        Button(
            Const("✅ Завершить задание"),
            id="submit_task",
            on_click=on_submit_task_button,
            when="can_submit",
        ),
        Back(Const("🔙 К списку задач")),
        getter=task_detail_getter,
        state=OperatorTaskStates.DETAIL,
    )

    tasks_dialog = Dialog(
        tasks_list_window,
        tasks_detail_window,
    )

    # Create dialogs
    student_tasks_dialog = Dialog(
        student_tasks_window,
        student_task_detail_window,
        student_submit_result_window,
    )

    operator_students_dialog = Dialog(
        operator_students_window,
    )

    operator_task_create_dialog = Dialog(
        create_task_title_window,
        create_task_description_window,
        create_task_start_date_window,
        create_task_due_date_window,
        create_task_confirm_window,
    )

    operator_review_dialog = Dialog(
        operator_submitted_tasks_window,
        operator_review_task_window,
        operator_rejection_comment_window,
    )

    return (
        student_tasks_dialog,
        operator_students_dialog,
        operator_task_create_dialog,
        operator_review_dialog,
        tasks_dialog,
    )
