from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    ROLE_CHOICE = State()
    FIRST_NAME = State()
    LAST_NAME = State()
    CONFIRM = State()
    SUCCESS = State()


class ProfileStates(StatesGroup):
    PROFILE = State()


class OperatorTaskStates(StatesGroup):
    LIST_TASKS = State()
    DETAIL = State()
    SUBMIT_RESULT = State()
    REVIEW_DETAIL = State()
    REJECT_COMMENT = State()


class StudentStates(StatesGroup):
    MY_TASKS = State()
    TASK_DETAIL = State()
    SUBMIT_TASK_RESULT = State()


class OperatorStudentsStates(StatesGroup):
    STUDENTS_LIST = State()
    STUDENT_TASKS = State()
    TASK_DETAIL = State()


class ClientGroupsStates(StatesGroup):
    GROUP_INFO = State()

class OperatorGroupsStates(StatesGroup):
    GROUP_LIST = State()
    GROUP_ACTIONS = State()
    GROUP_ADD_USER = State()


class OperatorTaskCreateStates(StatesGroup):
    CREATE_TASK_TITLE = State()
    CREATE_TASK_DESCRIPTION = State()
    CREATE_TASK_START_DATE = State()
    CREATE_TASK_DUE_DATE = State()
    CREATE_TASK_CONFIRM = State()


class OperatorGroupCreateStates(StatesGroup):
    CREATE_GROUP_NAME = State()
    CREATE_GROUP_DESCRIPTION = State()
    CREATE_GROUP_CONFIRM = State()

class OperatorAddStudentStates(StatesGroup):
    ADD_STUDENT_SELECT_GROUP = State()
    ADD_STUDENT_SELECT_STUDENT = State()
    ADD_STUDENT_CONFIRM = State()


class OperatorReviewStates(StatesGroup):
    SUBMITTED_TASKS = State()
    REVIEW_TASK_DETAIL = State()
    REJECT_TASK_COMMENT = State()
