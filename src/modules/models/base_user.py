from typing import Union

from aiogram import Bot
from sqlalchemy import select

from src.storages.sql.dependencies import database
from src.storages.sql.models import UserModel, users_table


class BaseUser:
    def __init__(self, telegram_id: int, role: str):
        self.telegram_id = telegram_id
        self.username = self._telegram_id_to_username()
        self.role = role

    def _telegram_id_to_username(self):
        user = database.fetch_one(
            select(users_table).where(users_table.c.idt == self.telegram_id),
            model=UserModel,
        )
        return user.user if user else "Unknown"

    def _get_username_by_telegram_id(self, telegram_id: Union[int, str]) -> str:
        user = database.fetch_one(
            select(users_table).where(users_table.c.idt == telegram_id),
            model=UserModel,
        )
        return user.user if user else "User not found"

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
        existing = database.fetch_one(
            select(users_table).where(users_table.c.idt == user_id),
            model=UserModel,
        )
        return existing is not None
