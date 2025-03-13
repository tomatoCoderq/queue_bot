import random
from typing import *
import os
import datetime

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command
from exceptiongroup import catch

from app.utils import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter

from app.utils.database import database


class BaseUser:
    def __init__(self, telegram_id: int, username: str, role: str):
        self.telegram_id = telegram_id
        self.username = self._telegram_id_to_username()
        self.role = role

    def _telegram_id_to_username(self):
        return database.fetchall("SELECT user FROM users WHERE idt=?", (self.telegram_id, ))

    async def send_message(self, bot: Bot, text: str, **kwargs):
        """Send a message to this user using the provided bot."""
        await bot.send_message(self.telegram_id, text, **kwargs)

    async def edit_message(self, bot: Bot, text: str, message_id: int, **kwargs):
        """Send a message to this user using the provided bot."""
        await bot.edit_message_text(text=text,
                                    chat_id=self.telegram_id,
                                    message_id=message_id,
                                    **kwargs)
