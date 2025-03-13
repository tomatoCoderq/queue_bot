import os
import datetime
import shutil
from pyexpat.errors import messages

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Dispatcher
from aiogram.filters import StateFilter, Command

from app.utils import keyboards
from aiogram import Bot, types, Router
from loguru import logger
from aiogram.filters import BaseFilter

from app.utils.database import database
from app.utils.keyboards import CallbackDataKeys
# from main import dp
# from app.handlers.teacher import create_idt_name_map
from app.utils.filters import IsStudent
from app.utils.messages import StudentMessages


def delete_file(data) -> None:
    messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0 or proceeed=1")
    students_ids = database.fetchall("SELECT idt FROM requests_queue WHERE proceeed=0 or proceeed=1")

    spdict = {messages_ids[i]: students_ids[i] for i in range(len(messages_ids))}

    try:
        document_name = [entry for entry in os.listdir(f'students_files/{spdict[int(data["id"])]}') if
                         entry.startswith(str(data['id']))]

        os.remove(f"students_files/{spdict[data['id']]}/{document_name[0]}")
        logger.success(f"Deleted file {spdict[data['id']]}/{document_name[0]}")
    except (OSError, KeyError) as e:
        logger.error(f"Occurred {e}")


def move_file(data: dict) -> None:
    """Move a file from the temporary folder to a permanent location."""
    messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0 or proceeed=1")
    students_ids = database.fetchall("SELECT idt FROM requests_queue WHERE proceeed=0 or proceeed=1")
    spdict = {messages_ids[i]: students_ids[i] for i in range(len(messages_ids))}
    try:
        directory = f'students_files/{spdict[int(data["id"])]}'
        document_name = [entry for entry in os.listdir(directory) if entry.startswith(str(data['id']))]
        if not os.path.exists(f"permanent/{spdict[data['id']]}"):
            os.makedirs(f"permanent/{spdict[data['id']]}")
        shutil.move(f"{directory}/{document_name[0]}", f"permanent/{spdict[data['id']]}/{document_name[0]}")
        logger.success(f"Moved file to permanent/{spdict[data['id']]}/{document_name[0]}")
    except (OSError, KeyError, shutil.Error) as e:
        logger.error(f"Error moving file: {e}")


async def download_file(message: types.Message, bot: Bot) -> None:
    # Check whether path exists. Otherwise, create new
    if not os.path.exists(f"students_files/{message.from_user.id}"):
        os.makedirs(f"students_files/{message.from_user.id}")
        logger.info(f"Created new dir {message.from_user.id} in students_files")

    try:
        message_id = database.fetchall("SELECT id FROM requests_queue "
                                       "WHERE proceeed=0 or proceeed=1")[-1]
        # message_id = [x[0] for x in cursor.execute("SELECT id FROM requests_queue "
        #                                            "WHERE proceeed=0 or proceeed=1").fetchall()][-1]
    except IndexError as e:
        logger.error("Error with message_id in download_file!")

    file_name = f"students_files/{message.from_user.id}/{message_id}?{datetime.date.today()}!{message.document.file_name}"
    open(file_name, "w").close()

    await bot.download(message.document, file_name)
    logger.success("Successfully downloaded document")