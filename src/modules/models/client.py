from typing import Union

from sqlalchemy import func, select

from src.modules.models.base_user import BaseUser
from src.modules.shared.messages import StudentMessages
from src.storages.sql.dependencies import database
from src.storages.sql.models import (
    PenaltyModel,
    StudentModel,
    TaskModel,
    penalty_table,
    students_table,
    tasks_table,
)


class Client(BaseUser):
    name: str
    surname: str
    username: str
    penalties: list[list]
    tasks: str

    penalties_reason_map = {
        "penalty_messy_desk": "Неубранное рабочее место",
        "penalty_no_shoes": "Отсутствие второй обуви"
    }

    def __init__(self, telegram_id: Union[int, str]):
        super().__init__(telegram_id, role="student")
        self.username = self._get_username_by_telegram_id(telegram_id)
        self.name, self.surname = self.__set_name_and_surname()
        self.penalties = self.__set_penalties()
        self.tasks = self.__get_tasks()

        # details as list (on the same screen or after pressing button)

    def __set_name_and_surname(self):
        student = database.fetch_one(
            select(students_table).where(students_table.c.idt == self.telegram_id),
            model=StudentModel,
        )
        if not student:
            return "Неизвестно", ""
        return student.name, student.surname

    def __set_penalties(self):
        return database.fetch_all(
            select(penalty_table).where(penalty_table.c.idt == self.telegram_id),
            model=PenaltyModel,
        )

    def __get_tasks(self):
        query = database.fetch_all(
            select(tasks_table)
            .where(tasks_table.c.idt == self.telegram_id)
            .where(tasks_table.c.status.in_([1, 5]))
            .where(func.date(tasks_table.c.start_time) == func.current_date())
            .order_by(tasks_table.c.id),
            model=TaskModel,
        )

        if not query:
            message_to_send = StudentMessages.NO_TASKS
            return message_to_send

        task = query[-1]
        message_to_send = (
            f"<b>Задачи на сегодня:</b>\n(1) {task.task_first}\n(2) {task.task_second}"
        )
        return message_to_send

    def get_penalties(self):
        self.penalties = self.__set_penalties()
        to_return = ""

        if len(self.penalties) == 0:
            return "Здесь пусто\n"

        fragments: list[str] = []
        for idx, penalty in enumerate(self.penalties):
            connector = "\n" if idx % 2 else " / "
            fragments.append(f"<b>ID:</b> {penalty.id} | {penalty.reason}{connector}")

        # Ensure output ends with a newline instead of a trailing slash
        if fragments and fragments[-1].endswith(" / "):
            fragments[-1] = fragments[-1][:-3] + "\n"

        to_return = "".join(fragments)

        return to_return

    def full_card(self) -> str:
        return (f"<b>{self.name} {self.surname}</b>\n"
                f"---\n"
                f"<b>Штрафы:</b> \n"
                f"{self.get_penalties()}"
                f"\n<b>Задачи:</b> \n"
                f"{self.tasks}")

        # return f"{self.name} {self.surname}"
