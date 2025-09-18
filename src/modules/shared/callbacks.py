"""Callback data keys shared across modules."""


class CallbackDataKeys:
    # Registration
    start_registration_client = "student"
    start_registration_operator = "teacher"

    # Student actions
    upload_detail = "send_piece"
    details_queue = "student_requests"
    tasks = "tasks"

    submit_tasks = "submit_tasks"
    close_tasks = "close_tasks"

    end_current_task = "end_current_task"
    continue_current_task = "continue_current_task"

    urgency_high = "high"
    urgency_medium = "medium"
    urgency_low = "low"

    back_to_main_student = "back_to_main_student"

    add_10_minutes = "10"
    add_15_minutes = "15"
    add_30_minutes = "30"

    change_current_task = "change_current_task"
    reject_current_task = "reject_current_task"

    task_one = "task_one"
    task_two = "task_two"

    penalties = "penalty"
    add_penalty = "add_penalty"
    remove_penalty = "remove_penalty"
    add_tasks_to_student = "add_tasks_to_student"

    # Inventory
    INVENTORY_ADD = "inventory_add"
    BACK_TO_INVENTORY = "back_to_inventory"
    TRANSFER_ITEM = "transfer_item"
    RETURN_ITEM = "return_item"
    STUDENT_EQUIPMENT = "student_equipment"

    # Teacher queues/actions
    details_queue_teacher = "details_queue_teacher"
    client_tasks = "client_tasks"

    open_queue = "check"
    history = "history"
    xlsx = "xlsx"

    sort_by_type = "sort_type"
    sort_by_date = "sort_date"
    sort_by_urgency = "sort_urgency"

    back_to_main_teacher = "back_to_main_teacher"
    back_to_details_teacher = "back_to_details_teacher"
    back_to_main_teacher_no_edit = "back_to_main_teacher_no_edit"
    back_to_tasks_teacher = "back_to_tasks_teacher"
    back_to_penalties_teacher = "back_to_penalties_teacher"
    back_to_queue = "back_to_queue"

    confirm_high_urgency = "accept_high_urgency"
    reject_high_urgency = "reject_high_urgency"
    accept_detail = "accept"
    reject_detail = "reject"

    accept_task = "accept_task"
    reject_task = "reject_task"

    accept_end_of_session = "accept_end_of_session"
    reject_end_of_session = "reject_end_of_session"

    end_task = "end"

    # Misc
    clients = "clients"
