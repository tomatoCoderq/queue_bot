from typing import *

from aiogram import Bot
from app.utils.database import database


class BaseUser:
    def __init__(self, telegram_id: int, role: str):
        self.telegram_id = telegram_id
        self.username = self._telegram_id_to_username()
        self.role = role

    def _telegram_id_to_username(self):
        return database.fetchall("SELECT user FROM users WHERE idt=?", (self.telegram_id,))

    def _get_username_by_telegram_id(self, telegram_id: Union[int, str]) -> str:
        result = database.fetchall("SELECT user FROM users WHERE idt = ?", (telegram_id,))
        return result[0] if result else "User not found"

    async def send_message(self, idt, bot: Bot, text: str, **kwargs):
        """Send a message to this user using the provided bot."""
        await bot.send_message(idt, text, **kwargs)

    async def edit_message(self, bot: Bot, text: str, message_id: int, **kwargs):
        """Send a message to this user using the provided bot."""
        await bot.edit_message_text(text=text,
                                    chat_id=self.telegram_id,
                                    message_id=message_id,
                                    **kwargs)

    @staticmethod
    def user_exists(user_id: int) -> bool:
        """Check if a user with the given ID exists in the users table."""
        result = database.fetchall("SELECT idt FROM users WHERE idt=?", (user_id,))
        return bool(result)

