from typing import Union

from sqlalchemy import select

from src.modules.models.base_user import BaseUser
from src.storages.sql.dependencies import database
from src.storages.sql.models import StudentModel, requests_queue_table, students_table


# Teacher Class: Inherits BaseUser and fixes role as 'teacher'
class Operator(BaseUser):
    def __init__(self, telegram_id: Union[int, str]):
        super().__init__(telegram_id, role="teacher")

    @staticmethod
    def get_idt_name_map() -> dict:
        records = database.fetch_all(
            select(
                requests_queue_table.c.idt.label("idt"),
                students_table.c.name.label("name"),
                students_table.c.surname.label("surname"),
            )
            .join(students_table, requests_queue_table.c.idt == students_table.c.idt)
            .distinct(),
            model=StudentModel,
        )
        return {record.idt: (record.name, record.surname) for record in records}

    @staticmethod
    def urgency_int_to_str(urgency: int) -> str:
        if urgency == 1:
            return "Высокая"
        elif urgency == 2:
            return "Средняя"
        elif urgency == 3:
            return "Низкая"
        return "Неизвестно"

    @staticmethod
    def status_int_to_str(status: int) -> str:
        if status == 0:
            return "Не в работе"
        elif status == 1:
            return "В работе"
        return "Неизвестно"
