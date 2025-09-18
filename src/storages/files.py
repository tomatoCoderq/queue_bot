import os
import datetime
import shutil

from sqlalchemy import select

from aiogram import Bot, types
from loguru import logger

from src.storages.sql.dependencies import database
from src.storages.sql.models import requests_queue_table
# from main import dp
# from app.handlers.teacher import create_idt_name_map


def delete_file(data) -> None:
    with database.session() as session:
       
        rows = session.execute(
            select(requests_queue_table.c.id, requests_queue_table.c.idt)
            .where(requests_queue_table.c.proceeed.in_([0, 1]))
        ).all()

    spdict = {row[0]: row[1] for row in rows}

    try:
        document_name = [entry for entry in os.listdir(f'students_files/{spdict[int(data["id"])]}') if
                         entry.startswith(str(data['id']))]

        os.remove(f"students_files/{spdict[data['id']]}/{document_name[0]}")
        logger.success(f"Deleted file {spdict[data['id']]}/{document_name[0]}")
    except (OSError, KeyError) as e:
        logger.error(f"Occurred {e}")


def move_file(data: dict) -> None:
    """Move a file from the temporary folder to a permanent location."""
    with database.session() as session:
        rows = session.execute(
            select(requests_queue_table.c.id, requests_queue_table.c.idt)
            .where(requests_queue_table.c.proceeed.in_([0, 1]))
        ).all()
    spdict = {row[0]: row[1] for row in rows}
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

    with database.session() as session:
        message_ids = session.scalars(
            select(requests_queue_table.c.id).where(requests_queue_table.c.proceeed.in_([0, 1]))
        ).all()

    if message_ids:
        message_id = message_ids[-1]
    else:
        logger.error("Error with message_id in download_file!")
        message_id = "unknown"

    file_name = f"students_files/{message.from_user.id}/{message_id}?{datetime.date.today()}!{message.document.file_name}"
    open(file_name, "w").close()

    await bot.download(message.document, file_name)
    logger.success("Successfully downloaded document")
