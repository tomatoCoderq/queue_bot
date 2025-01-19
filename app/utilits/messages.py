class StudentMessages:
    cancel_process = (
        "Процесс загрузки прерван.\nВыбирайте, <b>Клиент!</b>"
    )
    urgency_selection = (
        "<b>Внимание!</b> <i>Высокий приоритет</i> будет отправлен Оператору на обработку.\n"
        "<i>Средний приоритет</i> - деталь нужна вам завтра/послезавтра\n"
        "<i>Низкий приоритет</i> - экспериментальная деталь нужна вам в течение недели\n"
        "<i>Выберите <b>приоритет</b> задания: </i>"
    )
    priority_chosen = (
        "<b>Приоритет выбран!</b> Добавьте <i>описание</i> для детали: пожелания, уточнения и тд.\n"
        "Если таковых нет, пришлите прочерк"
    )
    invalid_priority_cancelled = (
        "Отправка задания была прервана. Начните новую отправку!"
    )
    description_accepted = (
        "<b>Описание принято!</b> Пришлите файл для печати/резки\n<b>Внимание!</b> "
        "Обрабатываются файлы <i>только</i> с расширением .stl или .dxf"
    )
    invalid_file_extension = (
        "<b>Неверное расширение файла!<b> Пришлите файл ещё раз"
    )
    request_queued = (
        "<b>Запрос с ID {request_id} отправлен в очередь</b>! Когда оператор возьмет его "
        "на печать/резку, вам отправят сообщение :)"
    )
    choose_next_action = (
        "Выбирайте, <b>Клиент!</b>"
    )


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
        "Вы не можете выбрать роль Оператора! Выберите другую роль"
    )
    student_provide_name = "Напишите Имя и Фамилию:\n<i>Например: Иван Иванов</i>"
    student_role_chosen = (
        "<b>Выбрана роль Клиента!</b> Чтобы получить больше информации напишите /help "
    )


class TeacherMessages:
    CANCEL_PROCESS = "Процесс загрузки прерван.\nВыбирайте, <b>Оператор!</b>"
    NO_ID_FOUND = "Такого ID <b>нет</b> в списке!. Попробуйте еще раз"
    REQUEST_ACCEPTED = "Ваша деталь с ID {id} принята на печать/резку"
    REQUEST_ALREADY_IN_WORK = "Уже в работе"
    REQUEST_NOT_IN_WORK = "Запрос еще не был принят в работу!"
    SEND_PHOTO_REPORT = "Пришлите <b>фотографию-отчет</b> результата печати/резки"
    PHOTO_SENT_TO_STUDENT = (
        "Фотография была отправлена <b>ученику</b>.\nЗапрос больше <b>не будет</b> отображаться в очереди"
    )
    CHOOSE_MAIN_TEACHER = "Выбирайте, Преподаватель"
    NO_REQUESTS = "Очередь пуста и запросов нет!"
    SELECT_REQUEST = "Напишите ID запроса, чтобы увидеть подробную информацию\n---\n"
    ID_ERROR = "<b>Произошла ошибка!</b> Пропишите /cancel"
