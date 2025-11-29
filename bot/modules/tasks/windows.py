from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Back, Row, Cancel
from aiogram_dialog.widgets.input import TextInput, MessageInput
from bot.modules.states import (
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
        # get_student_tasks_for_operator_data,
        tasks_list_getter,
        on_create_task_start,
        on_task_title_input,
        on_task_description_input,
        on_task_start_date_input,
        on_task_due_date_input,
        on_no_due_date,
        on_confirm_create_task,
        on_cancel_create_task,
        on_toggle_completed_tasks,
        task_detail_getter,
        # Quick start date handlers
        on_start_date_now,
        # Quick due date handlers
        on_due_date_1hour,
        on_due_date_2hours,   
        on_due_date_1day,
        on_add_file,
        on_proceed_all_files_added,
        get_files_data,
        on_file_received,
        # Getter for confirmation window
        # Sort handlers
        on_sort_by_start_date,
        on_sort_by_due_date,
        on_sort_by_status,
        on_sort_reset,
        on_submit_task_button,
        on_task_result_input,
        get_submitted_tasks_data,
        on_submitted_task_select,
        get_review_task_detail_data,
        on_approve_task,
        on_reject_task_button,
        on_rejection_comment_input,
        on_delete_task,
        on_view_task_files

    )

    # Window 3: Submit task result
    student_submit_result_window = Window(
        Const(
            "📝 <b>Отправка результата</b>\n\n"
            "Введите результат выполнения задания.\n"
            "Результат будет отправлен преподавателю на проверку.\n\n"
            "💡 <i>Опишите подробно что было сделано</i>"
        ),
        TextInput(
            id="result_input",
            on_success=on_task_result_input,
        ),
        Back(Const("🔙 Отмена")),
        state=OperatorTaskStates.SUBMIT_RESULT,
    )

    # ============ TASK CREATION WINDOWS (FOR OPERATOR) ============

    create_task_title_window = Window(
        Const("➕ <b>Создание задачи</b>\n\n"
              "📋 <b>Шаг 1 из 6:</b> Введите название задачи"),
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
            "➥ <b>Создание задачи</b>\n\n"
            "📋 <b>Шаг 2 из 6:</b> Введите описание задачи\n\n"
            "📌 <b>Название:</b> {dialog_data[task_title]}"
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
            "➕ <b>Создание задачи</b>\n\n"
            "📋 <b>Шаг 3 из 6:</b> Установите время начала\n\n"
            "📌 <b>Название:</b> {dialog_data[task_title]}\n"
            "📝 <b>Описание:</b> {dialog_data[task_description]}\n\n"
            "🕐 Выберите быстрый вариант или введите вручную:"
        ),
        Row(
            Button(
                Const("🕐 Сейчас"),
                id="start_now",
                on_click=on_start_date_now,
            )
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
            "➥ <b>Создание задачи</b>\n\n"
            "📋 <b>Шаг 4 из 6:</b> Установите дедлайн\n\n"
            "📌 <b>Название:</b> {dialog_data[task_title]}\n"
            "📝 <b>Описание:</b> {dialog_data[task_description]}\n"
            "🕐 <b>Время начала:</b> {dialog_data[task_start_date]}\n\n"
            "⏰ Выберите быстрый вариант или введите вручную:"
        ),
        Row(
            Button(
                Const("⏱ 1 час"),
                id="due_1hour",
                on_click=on_due_date_1hour,
            ),
            Button(
                Const("⏱ 2 часа"),
                id="due_2hours",
                on_click=on_due_date_2hours,
            ),
        ),
        Row(
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

    add_files_window = Window(
        Format(
            "📎 <b>Добавление файлов</b>\n\n"
            "📋 Шаг 5 из 6: Добавьте файлы к задаче\n"
            "📊 Загружено файлов: {files_count}\n\n"
            "💡 <i>Можно добавить фото, документы или пропустить шаг</i>"
        ),
        Row(
            Button(
                Const("📎 Добавить файл"),
                id="add_file_btn",
                on_click=on_add_file,
            ),
            Button(
                Const("➡️ Далее"),
                id="proceed_btn",
                on_click=on_proceed_all_files_added
            )
        ),
        Back(Const("🔙 Назад")),
        getter=get_files_data,
        state=OperatorTaskCreateStates.CREATE_TASK_WAIT_PHOTOS,
    )

    add_photo_window = Window(
        Const(
            "📷 <b>Ожидание файла</b>\n\n"
            "📎 Отправьте файл (фото или документ)\n"
            "✨ После отправки вы вернетесь к списку файлов"
        ),
        MessageInput(
            func=on_file_received,
            content_types=['photo', 'document']
        ),
        Back(Const("🔙 Отмена")),
        state=OperatorTaskCreateStates.CREATE_TASK_ADD_PHOTO,
    )

    create_task_confirm_window = Window(
        Format(
            "✅ <b>Подтвердите создание задачи</b>\n\n"
            "📌 <b>Название:</b> {dialog_data[task_title]}\n"
            "📝 <b>Описание:</b> {dialog_data[task_description]}\n"
            "📅 <b>Дата начала:</b> {dialog_data[task_start_date]}\n"
            "⏰ <b>Дедлайн:</b> {dialog_data[task_due_date]}\n"
            "📎 <b>Файлов добавлено:</b> {files_count}\n\n"
            # "{files_info}\n\n"
            "🎯 Создать задачу и назначить студенту?"
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
        getter=get_files_data,
        state=OperatorTaskCreateStates.CREATE_TASK_CONFIRM,
    )

    operator_submitted_tasks_window = Window(
        Format(
            "📝 <b>Задачи на проверке</b>\n\n"
            "📊 Всего задач: {tasks_count}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        ScrollingGroup(
            Select(
                Format("📝 {item[title]} {item[status_emoji]}"),
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
            "📋 <b>Проверка задачи</b>\n\n"
            "👤 <b>Студент:</b> {student_name}\n\n"
            "📌 <b>Название:</b> {task[title]}\n"
            "📝 <b>Описание:</b> {task[description]}\n"
            "📅 <b>Дата начала:</b> {task[start_date]}\n"
            "⏰ <b>Дедлайн:</b> {task[due_date]}\n\n"
            "✏️ <b>Результат студента:</b>\n<code>{task[result]}</code>\n"
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
                Format("📝 {item[title]} {item[status_emoji]}"),
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
            Const("Показать завершённые"),
            id="toggle_completed_op",
            on_click=on_toggle_completed_tasks,
        ),
        Button(
            Const("➕ Создать задачу"),
            id="create_task_btn",
            on_click=on_create_task_start,
            when="can_create_task",
        ),
        Cancel(Const("🔙 Назад")),
        # Button(
        #     Const("🔙 Назад"),
        #     on_click=lambda c, b, m: m.start(OperatorStudentsStates.STUDENTS_LIST
        # )
        state=OperatorTaskStates.LIST_TASKS,
        getter=tasks_list_getter,
    )
    tasks_detail_window = Window(
        Format(
            "📋 <b>Детали задачи</b>\n\n"
            "📌 <b>Название:</b> {task[title]}\n"
            "📝 <b>Описание:</b> {task[description]}\n"
            "📅 <b>Дата начала:</b> {task[start_date]}\n"
            "⏰ <b>Дедлайн:</b> {task[due_date]}\n"
            "🎯 <b>Статус:</b> {task[status_display]}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        Format(
            "❌ <b>Комментарий преподавателя:</b>\n{task[rejection_comment]}\n\n",
            when="task[has_rejection]"
        ),
        Format(
            "⚠️ {overdue_warning}\n\n",
            when="is_overdue"
        ),
        Button(
            Const("Файлы задачи"),
            id="view_task_files",
            on_click=on_view_task_files,
        ),
        Button(
            Const("🗑 Удалить задачу"),
            id="delete_task",
            on_click=on_delete_task,
            when="operator",
        ),
        Button(
            Const("✅ Завершить задание"),
            id="submit_task",
            on_click=on_submit_task_button,
            when="can_submit",
        ),
        Button(
            Format("🔙 {back_text}"),
            id="back_button",
            on_click=lambda c, b, m: m.back(),
        ),
        getter=task_detail_getter,
        state=OperatorTaskStates.DETAIL,
    )

    tasks_dialog = Dialog(
        tasks_list_window,
        tasks_detail_window,
        student_submit_result_window,
    )

    operator_task_create_dialog = Dialog(
        create_task_title_window,
        create_task_description_window,
        create_task_start_date_window,
        create_task_due_date_window,
        add_files_window,
        add_photo_window,
        create_task_confirm_window,
    )

    operator_review_dialog = Dialog(
        operator_submitted_tasks_window,
        operator_review_task_window,
        operator_rejection_comment_window,
    )

    return (
        operator_task_create_dialog,
        operator_review_dialog,
        tasks_dialog,
    )
