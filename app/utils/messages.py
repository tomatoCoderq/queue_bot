class KeyboardTitles:
    # Titles for registration
    start_registration_client = "👤 Клиент"
    start_registration_operator = "👥 Оператор"

    # Titles for student main actions
    upload_detail = "⬇️ Загрузить на печать/резку"
    task_queue = "📂 Очередь заданий"
    tasks = "📆 Задачи"

    # Titles for tasks
    submit_tasks = "📌 Установить задачи"
    close_tasks = "🆗 Закончить на сегодня"
    end_current_task = "❌ Завершить текущую задачу"
    continue_current_task = "🔄 Продолжить задачу"

    # Titles for urgency levels
    urgency_high = "🔴 Высокий"
    urgency_medium = "🟠 Средний"
    urgency_low = "🟢 Низкий"

    details_queue_teacher = "📂 Задания"
    client_tasks = "📆 Задачи"

    # Titles for teacher actions
    open_queue = "📂 Открыть очередь"
    history = "⏮️ История отклонённых запросов"
    get_xlsx = "📒 Таблица заданий"
    sort_by_type = "1️⃣ Сортировка по типу"
    sort_by_date = "2️⃣ Сортировка по дате"
    sort_by_urgency = "3️⃣ Сортировка по срочности"
    back_to_main_teacher = "⬅️ Назад"

    # Titles for teacher process actions
    confirm_high_urgency = "✅ Подтвердить"
    reject_high_urgency = "❌ Отклонить"
    accept_task = "✅ Принять"
    reject_task = "❌ Отклонить"
    accept_detail_already_accepted = "⬛️ Принять"
    reject_detail_already_accepted = "⬛️ Отклонить"
    end_detail = "⬛️ Завершить печать/резку"
    end_detail_accepted = "🟩 Завершить печать/резку"
    back_to_queue = "⬅️ Назад"

    # Back to main menu for student
    back_to_main_student = "⬅️ Назад"

    # Titles for tasks actions student
    add_10_minutes = "10"
    add_15_minutes = "15"
    add_30_minutes = "30"

    # Titles for tasks actions teacher
    change_current_task = "🔄 Поменять задание"
    first_task = "1️⃣"
    second_task = "2️⃣"
    reject_current_task = "🚫 Отклонить задание"

    penalties = "⭕️ Штрафы"
    add_tasks_to_student = "➕ Добавить задачи"
    add_penalty = "➕"
    remove_penalty = "➖"

    BACK = "⬅️ Назад"
    ADD_DETAIL = "➕ Добавить"
    TRANSFER = "🔄 Передать"
    RETURN = "↩️ Вернуть"
    INVENTORY = "<b>Инвентарь</b>:"
    MAIN_MENU = "<b>Главное меню</b>"


class StudentMessages:
    cancel_process = "🟥 <b>Процесс загрузки прерван.</b>\nВыбирайте, <b>Клиент!</b>"
    urgency_selection = (
        "<b>Внимание!</b> <i>Высокий приоритет</i> будет отправлен Оператору на обработку.\n"
        "<i>Средний приоритет</i> – деталь нужна вам завтра/послезавтра.\n"
        "<i>Низкий приоритет</i> – экспериментальная деталь нужна в течение недели.\n"
        "<i>Выберите <b>приоритет</b> задания:</i>"
    )
    priority_chosen = (
        "<b>Приоритет выбран!</b>\n"
        "Напишите количество деталей для печати/резки.\n"
        "<b>Внимание:</b> ответ должен содержать только цифры."
    )
    AMOUNT_ACCEPTED = (
        "<b>Количество деталей принято!</b>\n"
        "Добавьте <i>описание</i> для детали (пожелания, уточнения и т.д.).\n"
        "Если описания нет, пришлите прочерк."
    )
    INVALID_AMOUNT_INPUT = "🟥 <b>Ошибка:</b> сообщение должно содержать <b>только цифры</b>!"
    invalid_priority_cancelled = "🟥 Отправка задания прервана. Начните новую отправку!"
    description_accepted = (
        "<b>Описание принято!</b>\n"
        "Пришлите файл для печати/резки.\n"
        "<b>Внимание:</b> поддерживаются файлы только с расширениями <i>.stl</i> или <i>.dxf</i>."
    )
    invalid_file_extension = "🟥 <b>Ошибка:</b> неверное расширение файла! Пришлите файл ещё раз."
    request_queued = (
        "<b>Запрос с ID {request_id} отправлен в очередь!</b>\n"
        "Как только оператор возьмёт его на печать/резку, вам придёт уведомление."
    )
    choose_next_action = "Выбирайте, <b>Клиент!</b>"
    HIGH_URGENCY_ACCEPTED = "🟩 <b>Высокий приоритет одобрен!</b>"
    HIGH_URGENCY_REJECTED = "🟥 <b>Высокий приоритет не одобрен!</b>"
    SUCESSFULLY_DELETED = "✅ Ваш запрос удалён!"
    NO_ID_FOUND = (
        "🟥 <b>Ошибка:</b> такого ID <b>нет</b> или деталь уже принята в работу.\n"
        "Попробуйте ещё раз или отправьте /cancel для возврата в главное меню."
    )
    NO_TASKS = "ℹ️ Задачи отсутствуют!\n"
    WRITE_FIRST_TASK_TO_SUBMIT = (
        "Напишите задачу на <b>первый</b> час:\n"
        "<b>Внимание:</b> выбирайте аккуратно и проконсультируйтесь с преподавателем – изменить задачу не получится в течение часа."
    )
    WRITE_SECOND_TASK_TO_SUBMIT = "Напишите задачу на <b>следующий</b> час:\n"
    SEND_TO_OPERATOR_TASKS = "{task_one}\n{task_two}  <b>ID:</b> {database.fetchall('select id from tasks order by id desc')[0]}"
    SUCESSFULLY_ADDED_TASKS = (
        "✅ Задачи отправлены оператору!\n"
        "Ожидайте фидбек.\n"
        "<b>ID запроса:</b> {request_id}"
    )
    INVITE_OPERATOR_FOR_APPROVE = "⏳ Сейчас подойдёт оператор для подтверждения запроса!"
    ASK_OPERATOR_TO_COME_FOR_APPROVE = "🔔 Подойдите к апруву запроса с\n<b>ID:</b> {database.last_added_id()}"
    TASKS_NOT_SET = "ℹ️ Задачи на сегодня ещё не установлены."

    NO_EQUIPMENT_FOUND = "<b>⚠️ Не найдено деталей на вашем аккаунте!</b>"
    YOUR_EQUIPMENT_HEADER = "<b>📦 Ваши детали:</b>\n\n"
    EQUIPMENT_ITEM_FORMAT = "🔹 <b>ID:</b> {detail_id}  |  <b>Name:</b> {name}  |  <b>Цена:</b> {price}\n"
    CHOOSE_NEXT_ACTION = "<b>Меню</b>"
    ADD_DETAIL_PROMPT = "<b>Введите название детали</b> и <b>цену</b> через запятую.\nПример: <i>Arduino Mega, 1500</i>"
    INVALID_DETAIL_FORMAT = "<b>Неверный формат!</b> Введите данные в формате: <i>Название, цена</i>"
    DETAIL_ADDED_CONFIRM = "✅ Деталь «<b>{name}</b>» успешно добавлена со стоимостью <b>{price}</b>."


class LoginMessages:
    welcome_teacher = "👋 С возвращением, <b>Оператор!</b>"
    welcome_student = "👋 С возвращением, <b>Клиент!</b>"


class RegistrationMessages:
    welcome_message = (
        "👋 Привет! Добро пожаловать в <b>DigitalQueue</b> – удобный бот для цифровых очередей.\n"
        "<i>Выберите свою роль:</i>"
    )
    teacher_role_chosen = "<b>✅ Роль Оператора выбрана!</b> Для подробностей введите /help."
    teacher_registration_failed = "🟥 <b>Ошибка:</b> вы не можете выбрать роль Оператора! Выберите другую роль."
    student_provide_name = "✏️ Напишите Имя и Фамилию:\n<i>Например: Иван Иванов</i>"
    student_role_chosen = "<b>✅ Роль Клиента выбрана!</b> Для подробностей введите /help."


class TeacherMessages:
    CANCEL_PROCESS = "🟥 <b>Процесс загрузки прерван.</b>\nВыбирайте, <b>Оператор!</b>"
    NO_ID_FOUND = (
        "🟥 <b>Ошибка:</b> такого ID <b>нет</b> в списке.\n"
        "Попробуйте ещё раз или отправьте /cancel для возврата в главное меню."
    )
    REQUEST_ACCEPTED = "🟩 Ваша деталь с <b>ID {id}</b> <b>принята</b> на печать/резку."
    REQUEST_REJECTED = (
        "🟥 Ваша деталь с <b>ID {id}</b> <b>отклонена</b>!\n"
        "Проконсультируйтесь с преподавателем и переделайте деталь."
    )
    REQUEST_ALREADY_IN_WORK = "ℹ️ Деталь уже в работе."
    REQUEST_NOT_IN_WORK = "ℹ️ Запрос ещё не принят в работу!"
    SEND_SIZE_REPORT = (
        "📏 Пришлите длину и ширину (в см) прямоугольника, из которого вырезали деталь.\n"
        "<b>Внимание:</b> ответ должен состоять из двух чисел."
    )
    SEND_WEIGHT_REPORT = (
        "⚖️ Пришлите массу готовой детали.\n"
        "<b>Внимание:</b> ответ должен состоять только из цифр."
    )
    SEND_PHOTO_REPORT = "📸 Пришлите <b>фотографию-отчет</b> результата печати/резки."
    PHOTO_SENT_TO_STUDENT = (
        "✅ Фотография отправлена <b>ученику</b>.\n"
        "Запрос больше не будет отображаться в очереди."
    )
    INVALID_SIZE_INPUT = "🟥 <b>Ошибка:</b> отправьте <b>два числа</b>! Попробуйте ещё раз."
    CHOOSE_MAIN_TEACHER = "Выбирайте, <b>Оператор!</b>"
    NO_REQUESTS = "ℹ️ Очередь пуста, запросов нет."
    SELECT_REQUEST = "✏️ Напишите ID запроса для подробной информации:\n---\n"
    ID_ERROR = "🟥 <b>Ошибка:</b> произошла ошибка – отправьте /cancel."
    ENTER_USER_ID = "Введите <b>ID нужного пользователя</b>:\n"
    NO_PENALTIES = "🟥 <b>Ошибка:</b> штрафов не найдено!"
    ENTER_PENALTY_REASON = "📝 Напишите причины штрафа:"
    PENALTY_ADDED = "🟩 Штраф успешно добавлен!"
    ENTER_PENALTY_ID_TO_DELETE = "Введите <b>ID штрафа для удаления</b>:"
    ONLY_NUMBERS_ALLOWED = "🟥 <b>Ошибка:</b> сообщение должно содержать только цифры!"
    PENALTY_DELETED = "🟩 Штраф удалён!"
