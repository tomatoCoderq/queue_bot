"""
Утилиты для безопасного форматирования текста в боте
"""
from html import escape
from typing import Any, Dict


def safe_format_student_name(student: Dict[str, Any]) -> str:
    """
    Безопасно форматирует имя студента с экранированием HTML
    """
    first_name = escape(student.get('first_name', ''))
    last_name = escape(student.get('last_name', ''))
    return f"{first_name} {last_name}".strip()


def safe_format_task_title(task_title: str) -> str:
    """
    Безопасно форматирует название задачи с экранированием HTML
    """
    return escape(str(task_title))


def safe_format_group_name(group_name: str) -> str:
    """
    Безопасно форматирует название группы с экранированием HTML
    """
    return escape(str(group_name))


def safe_format_comment(comment: str) -> str:
    """
    Безопасно форматирует комментарий с экранированием HTML
    """
    return escape(str(comment))