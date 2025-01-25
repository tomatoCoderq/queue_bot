class KeyboardTitles:
    # Titles for registration
    start_registration_client = "Клиент"
    start_registration_operator = "Оператор"

    # Titles for student main actions
    upload_task = "⬇️Загрузить на печать/резку"
    task_queue = "📂Очередь заданий"

    # Titles for urgency levels
    urgency_high = "🔴Высокий"
    urgency_medium = "🟠Средний"
    urgency_low = "🟢Низкий"

    # Titles for teacher actions
    open_queue = "📂Открыть очередь"
    sort_by_type = "1️⃣Сортировка по типу"
    sort_by_date = "2️⃣Сортировка по дате"
    sort_by_urgency = "3️⃣Сортировка по срочности"
    back_to_main_teacher = "⬅️Назад"

    # Titles for teacher process actions
    confirm_high_urgency = "✅Подтвердить"
    reject_high_urgency = "❌Отклонить"
    accept_task = "✅Принять"
    reject_task = "❌Отклонить"
    end_task = "⬛️Закончить печать/резку"
    back_to_queue = "⬅️Назад"

    # Back to main menu for student
    back_to_main_student = "⬅️Назад"


class StudentMessages:
    cancel_process = (
        "🟥Процесс загрузки прерван.\nВыбирайте, <b>Клиент!</b>"
    )
    urgency_selection = (
        "<b>Внимание!</b> <i>Высокий приоритет</i> будет отправлен Оператору на обработку.\n"
        "<i>Средний приоритет</i> - деталь нужна вам завтра/послезавтра\n"
        "<i>Низкий приоритет</i> - экспериментальная деталь нужна вам в течение недели\n"
        "<i>Выберите <b>приоритет</b> задания: </i>"
    )

    priority_chosen = (
        "<b>Приоритет выбран!</b> Напишите количество деталей для печати/резки\n"
        "<b>Внимание!</b> Ответ должен состоять только из цифр"
    )

    AMOUNT_ACCEPTED = (
        "<b>Количество деталей принято!</b> Добавьте <i>описание</i> для детали: пожелания, уточнения и тд.\n "
        "Если таковых нет, пришлите прочерк")

    INVALID_AMOUNT_INPUT = "🟥Отправьте сообщение, которое содержит <b>только цифры!</b>"

    invalid_priority_cancelled = (
        "🟥Отправка задания была прервана. Начните новую отправку!"
    )
    description_accepted = (
        "<b>Описание принято!</b> Пришлите файл для печати/резки\n<b>Внимание!</b> "
        "Обрабатываются файлы <i>только</i> с расширением .stl или .dxf\n"
    )
    invalid_file_extension = (
        "<b>🟥Неверное расширение файла!<b> Пришлите файл ещё раз"
    )
    request_queued = (
        "<b>Запрос с ID {request_id} отправлен в очередь</b>! Когда оператор возьмет его "
        "на печать/резку, вам отправят сообщение :)"
    )
    choose_next_action = (
        "Выбирайте, <b>Клиент!</b>"
    )

    HIGH_URGENCY_ACCEPTED = "🟩Высокий приоритет одобрен!"
    HIGH_URGENCY_REJECTED = "🟥Высокий приоритет не одобрен!"
    SUCESSFULLY_DELETED = "Ваш запрос удален!"


class LoginMessages:
    welcome_teacher = (
        "С возвращением, <b>Оператор!</b>"
    )
    welcome_student = (
        "С возвращением, <b>Клиент!</b>"
    )


class RegistrationMessages:
    welcome_message = (
        "Привет! Это <b>DigitalQueue</b> бот для создания удобной цифровой очереди. "
        "\n<i>Выберите одну из доступных ролей:</i>"
    )
    teacher_role_chosen = (
        "<b>Выбрана роль Оператора!</b> Чтобы получить больше информации напишите /help"
    )
    teacher_registration_failed = (
        "🟥Вы не можете выбрать роль Оператора! Выберите другую роль"
    )
    student_provide_name = "Напишите Имя и Фамилию:\n<i>Например: Иван Иванов</i>"
    student_role_chosen = (
        "<b>Выбрана роль Клиента!</b> Чтобы получить больше информации напишите /help "
    )


class TeacherMessages:
    CANCEL_PROCESS = "🟥Процесс загрузки прерван.\nВыбирайте, <b>Оператор!</b>"
    NO_ID_FOUND = ("🟥Такого ID <b>нет</b> в списке!. Попробуйте еще раз\nЕсли вы хотите вернуться в главное меню, "
                   "пропишите /cancel")
    REQUEST_ACCEPTED = "🟩Ваша деталь с ID {id} <b>принята</b> на печать/резку"
    REQUEST_REJECTED = "🟥Ваша деталь с ID {id} <b>отклонена</b>! Проконсультируйтесь с преподавателем и переделайте деталь"
    REQUEST_ALREADY_IN_WORK = "Уже в работе"
    REQUEST_NOT_IN_WORK = "Запрос еще не был принят в работу!"
    SEND_SIZE_REPORT = ("Пришлите длину и ширину (в сантиметрах) прямоугольника, из которого вырезали деталь.\n"
                        "<b>Внимание!</b> Ответ должен состоять только из двух чисел")
    SEND_WEIGHT_REPORT = ("Пришлите массу готовой детали.\n"
                          "<b>Внимание!</b> Ответ должен состоять только из цифр")
    SEND_PHOTO_REPORT = "Пришлите <b>фотографию-отчет</b> результата печати/резки"
    PHOTO_SENT_TO_STUDENT = (
        "Фотография была отправлена <b>ученику</b>.\nЗапрос больше <b>не будет</b> отображаться в очереди"
    )
    INVALID_SIZE_INPUT = "🟥Вы должны отправить <b>два числа</b>! Попробуйте еще раз"
    CHOOSE_MAIN_TEACHER = "Выбирайте, Оператор"
    NO_REQUESTS = "Очередь пуста и запросов нет!"
    SELECT_REQUEST = "Напишите ID запроса, чтобы увидеть подробную информацию\n---\n"
    ID_ERROR = "<b>🟥Произошла ошибка!</b> Пропишите /cancel"

