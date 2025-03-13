import os
import datetime

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
from app.utils.filters import IsStudent
from app.utils.messages import StudentMessages

from app.models.client import Client

from app.fsm_states.client_states import SendPiece


# --- StudentManager Class ---
class ClientManager:
    def __init__(self, client: Client):
        self.client = client

    async def cancel_upload(self, message: types.Message, state: FSMContext):
        """Cancel the current upload process and return to main student menu."""
        await message.answer(
            StudentMessages.cancel_process,
            reply_markup=keyboards.keyboard_main_student(),
            parse_mode=ParseMode.HTML,
        )
        await state.clear()

    async def initiate_send_piece(self, callback: types.CallbackQuery, state: FSMContext):
        """Start the piece submission process by showing urgency options."""
        await callback.message.edit_text(
            StudentMessages.urgency_selection,
            reply_markup=keyboards.keyboard_urgency_student(),
            parse_mode=ParseMode.HTML,
        )
        await state.set_state(SendPiece.waiting_urgency)
        logger.info(f"{callback.message.from_user.username} set state: SendPiece.waiting_urgency")
        await callback.answer()

    async def process_urgency(self, callback: types.CallbackQuery, state: FSMContext):
        """Process the urgency selection and update the FSM state."""
        urgency_data = callback.data.lower()
        if urgency_data == "high":
            await state.update_data(urgency=2, to_approve_urgency=True)
        elif urgency_data == "medium":
            await state.update_data(urgency=2)
        elif urgency_data == "low":
            await state.update_data(urgency=3)
        logger.info(f"Updated urgency: {callback.data}")
        await state.set_state(SendPiece.waiting_amount)
        await callback.message.edit_text(StudentMessages.priority_chosen, parse_mode=ParseMode.HTML)
        await callback.answer()

    async def process_amount(self, message: types.Message, state: FSMContext):
        """Process the numeric amount input."""
        if not message.text.isdigit():
            await message.answer(StudentMessages.INVALID_AMOUNT_INPUT)
            return  # Optionally allow retry without state change
        await message.answer(StudentMessages.AMOUNT_ACCEPTED)
        await state.update_data(amount=message.text)
        await state.set_state(SendPiece.waiting_comments)
        logger.info(f"{message.from_user.username} set amount: {message.text}")

    async def process_comments(self, message: types.Message, state: FSMContext):
        """Process the additional comments/description."""
        await state.update_data(text=message.text)
        await state.set_state(SendPiece.waiting_file)
        logger.info(f"{message.from_user.username} provided comments: {message.text}")
        await message.reply(StudentMessages.description_accepted, parse_mode=ParseMode.HTML)

    async def process_file_upload(self, message: types.Message, state: FSMContext, bot: Bot):
        """Validate the uploaded file, record the request in the database, and download the file."""
        file_type = message.document.file_name[-3:].lower()
        if file_type not in {"stl", "dxf"}:
            logger.error(f"Wrong file type: {file_type}")
            await message.reply(StudentMessages.invalid_file_extension, parse_mode=ParseMode.HTML)
            return
        data = await state.get_data()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Prepare values for insertion into the requests_queue table.
        to_add = [
            self.client.telegram_id,
            data["urgency"],
            file_type,
            0,  # initial status
            now_str,
            data["text"],
            data["amount"],
            message.document.file_name[:-4],
            0,  # shift count
            0  # additional field if needed
        ]
        database.execute(
            "INSERT INTO requests_queue VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            to_add,
        )
        logger.success(f"Added request from {message.from_user.username} to requests_queue")
        # Retrieve the new request ID (assumed to be the last inserted).
        request_id = database.fetchall("SELECT id FROM requests_queue")[-1]
        await message.reply(
            StudentMessages.request_queued.format(request_id=request_id),
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.keyboard_main_student()
        )
        await self.download_file(message, bot)
        await state.clear()
        logger.info("SendPiece FSM cleared after file upload.")

    async def download_file(self, message: types.Message, bot: Bot) -> None:
        """Download the student's file into a local directory."""
        student_dir = f"students_files/{message.from_user.id}"
        if not os.path.exists(student_dir):
            os.makedirs(student_dir)
            logger.info(f"Created directory: {student_dir}")
        try:
            request_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0 or proceeed=1")
            message_id = request_ids[-1]
        except IndexError:
            logger.error("Error obtaining request ID for file download!")
            message_id = "unknown"
        file_name = f"{student_dir}/{message_id}?{datetime.date.today()}!{message.document.file_name}"
        open(file_name, "w").close()
        await bot.download(message.document, file_name)
        logger.success("File successfully downloaded.")

    async def back_to_main_student(self, callback: types.CallbackQuery, state: FSMContext):
        """Return the student to the main menu."""
        await callback.message.edit_text(
            StudentMessages.choose_next_action,
            reply_markup=keyboards.keyboard_main_student(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()
        await callback.answer()

    async def process_high_urgency_decision(self, callback: types.CallbackQuery):
        """
        Process high urgency confirmation/rejection from a callback.
        (This example assumes the request ID is extracted from the message text.)
        """
        if callback.data == "confirm_high_urgency":
            id_to_change = callback.message.text.split()[1]
            database.execute("UPDATE requests_queue SET urgency=? WHERE id=?", (1, id_to_change))
            logger.success("High urgency confirmed; urgency updated.")
            await callback.answer(StudentMessages.HIGH_URGENCY_ACCEPTED)
            await callback.message.delete()
        else:
            await callback.answer(StudentMessages.HIGH_URGENCY_REJECTED)
            await callback.message.delete()


class ClientManagerTasks:
    None