from dataclasses import dataclass, field
from datetime import datetime
from typing import Union

from app.models.base_user import BaseUser
from app.utils.database import database
from app.utils.messages import StudentMessages


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
        return database.fetchall_multiple("SELECT name, surname FROM students WHERE idt=?", (self.telegram_id,))[-1]

    def __set_penalties(self):
        return database.fetchall_multiple("SELECT id, reason FROM penalty WHERE idt=?", (self.telegram_id,))

    def __get_tasks(self):
        query = database.fetchall_multiple(
            f"SELECT * from tasks where idt=? and (status=1 or status=5) and SUBSTR(start_time, 1, 10)=DATE('now', 'utc')",
            (self.telegram_id,))
        print(database.fetchall(
            f"Select * from tasks where SUBSTR(start_time, 1, 10)=DATE('now', 'utc') and (status=1 or status=5) and idt=?",
            (str(self.telegram_id),)))
        print("DATENOW", database.fetchall_multiple("SELECT DATE('now')"))

        print("from", query)

        if len(query) == 0:
            message_to_send = StudentMessages.NO_TASKS
            return message_to_send

        query = query[-1]

        message_to_send = f"<b>Задачи на сегодня:</b>\n(1) {query[2]}\n(2) {query[3]}"
        return message_to_send

    def get_penalties(self):
        to_return = ""

        if len(self.penalties) == 0:
            return "Здесь пусто\n"

        for i in range(len(self.penalties)):
            if i % 2 != 0:
                to_return += f"<b>ID:</b> {self.penalties[i][0]} | {self.penalties[i][1]}\n"
            else:
                to_return += f"<b>ID:</b> {self.penalties[i][0]} | {self.penalties[i][1]} / "

        return to_return

    def full_card(self) -> str:
        return (f"<b>{self.name} {self.surname}</b>\n"
                f"---\n"
                f"<b>Штрафы:</b> \n"
                f"{self.get_penalties()}"
                f"\n<b>Задачи:</b> \n"
                f"{self.tasks}")

        # return f"{self.name} {self.surname}"
