from app.utils.database import database
from app.models.base_user import BaseUser


# Teacher Class: Inherits BaseUser and fixes role as 'teacher'
class Operator(BaseUser):
    def __init__(self, telegram_id: int, username: str):
        super().__init__(telegram_id, username, role="teacher")

    @staticmethod
    def get_idt_name_map() -> dict:
        """
        Returns a mapping from client IDs to (name, surname)
        by joining requests_queue and students.
        """
        database.execute("""
            SELECT requests_queue.idt, students.name, students.surname 
            FROM requests_queue 
            INNER JOIN students ON requests_queue.idt = students.idt
        """)
        return {row[0]: (row[1], row[2]) for row in database.cursor.fetchall()}

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
