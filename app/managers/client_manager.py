import os
import datetime

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from app.models.operator import Operator
from app.utils import keyboards
from aiogram import Bot, types
from loguru import logger

from app.utils.database import database
from app.utils.files import delete_file
from app.utils.messages import StudentMessages

from app.models.client import Client

from app.fsm_states.client_states import SendPiece, DeleteOwnQueue


class ClientManager:
    def __init__(self, client: Client):
        self.client = client

    def _generate_message_with_details(self, students_messages) -> str:
        message_to_send = [
            (f"<b>ID</b>: {students_messages[i][0]}\n"
             f"<b>Файл</b>: {students_messages[i][8]}.{students_messages[i][3]}\n"
             f"<b>Статус</b>: {Operator.status_int_to_str(students_messages[i][4])}\n---\n") for i in
            range(len(students_messages))]

        s = ('Если вы хотите удалить один из своих запросов, введите его ID! '
             'Удаляйте только неудачные или неправильно отправленные детали.\n'
             'Очередь заданий: \n---\n')
        if len(message_to_send) == 0:
            s += "Очередь заданий пуста!"
        else:
            for a in message_to_send:
                s += a
        return s


# --- StudentManager Class ---
class ClientManagerDetails(ClientManager):
    def __init__(self, client: Client):
        super().__init__(client)

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

        await state.update_data(file_type=message.document.file_name[-3:].lower())
        await state.update_data(file_name=message.document.file_name[:-4])

        if file_type == "stl":
            await message.answer("<b>Укажите вес детали (его можно посмотреть в слайсере) (в граммах)</b>:", parse_mode=ParseMode.HTML)
        else:
            await message.answer("<b>Укажите размеры прямоугольника, который вы используете для вырезания детали, в мм (ширина высота)</b>, например: <i>150 200</i>",
                                 parse_mode=ParseMode.HTML)
        old_file_name = await self.download_file(message, bot)
        await state.update_data(old_file_name=old_file_name)

        await state.set_state(SendPiece.waiting_param)
        logger.info("SendPiece FSM cleared after file upload.")

    async def download_file(self, message: types.Message, bot: Bot) -> str:
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

        return file_name

    async def rename_file(self, old_file_name, message: types.Message, state: FSMContext):
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

        data = await state.get_data()

        file_name = f"{student_dir}/{message_id}?{datetime.date.today()}!{data['file_name']}.{data['file_type']}"

        os.rename(old_file_name, file_name)
        logger.success("File successfully renamed.")

    async def process_detail_parameter(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        file_type = data.get("file_type")

        if file_type == "stl":
            if not message.text.isdigit():
                await message.answer("❌ Введите числовое значение веса (в граммах).")
                return
            value = int(message.text)
        elif file_type == "dxf":
            parts = message.text.strip().split()
            if len(parts) != 2 or not all(part.isdigit() for part in parts):
                await message.answer("❌ Введите два числа: ширину и высоту в мм.")
                return
            width, height = map(int, parts)
            value = width * height  # Area

        data = await state.get_data()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        to_add = [
            self.client.telegram_id,
            data["urgency"],
            file_type,
            0,  # initial status
            now_str,
            data["text"],
            data["amount"],
            data["file_name"],
            value,
            0  # additional field if needed
        ]

        database.execute(
            "INSERT INTO requests_queue VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            to_add,
        )
        logger.success(f"Added request from {message.from_user.username} to requests_queue")

        request_id = database.fetchall("SELECT id FROM requests_queue")[-1]

        await self.rename_file(data['old_file_name'], message, state)

        await message.reply(
            StudentMessages.request_queued.format(request_id=request_id),
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.keyboard_main_student()
        )

        await state.clear()

    async def process_high_urgency_decision(self, callback: types.CallbackQuery):
        if callback.data == "confirm_high_urgency":
            id_to_change = callback.message.text.split()[1]
            database.execute("UPDATE requests_queue SET urgency=? WHERE id=?", (1, id_to_change))
            logger.success("High urgency confirmed; urgency updated.")
            await callback.answer(StudentMessages.HIGH_URGENCY_ACCEPTED)
            await callback.message.delete()
        else:
            await callback.answer(StudentMessages.HIGH_URGENCY_REJECTED)
            await callback.message.delete()

    async def student_requests(self, callback: types.CallbackQuery, state: FSMContext):
        students_messages = database.fetchall_multiple(f"SELECT * FROM requests_queue "
                                                       f"WHERE proceeed!=2 and proceeed!=4 "
                                                       f"AND idt={callback.from_user.id}")

        await callback.message.edit_text(self._generate_message_with_details(students_messages),
                                         reply_markup=keyboards.keyboard_back_to_main_student(),
                                         parse_mode=ParseMode.HTML)
        await callback.answer()
        await state.set_state(DeleteOwnQueue.get_id_to_delete)
        await state.update_data(msg_id=callback.message.message_id)

    async def get_id_to_delete(self, message: types.Message, state: FSMContext, bot: Bot):
        messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0")
        data = await state.get_data()

        if not message.text.isdigit() or int(message.text) not in messages_ids:
            await message.reply(StudentMessages.NO_ID_FOUND, parse_mode=ParseMode.HTML)
            logger.error(f"Wrong id was written by {message.from_user.username}")
            return self.get_id_to_delete

        await bot.delete_message(message.chat.id, data['msg_id'])
        # await message.delete()
        delete_file({"id": int(message.text)})
        database.execute(f"UPDATE requests_queue SET proceeed=2 WHERE id=?", (message.text,))
        await message.answer(StudentMessages.SUCESSFULLY_DELETED, reply_markup=keyboards.keyboard_main_student())
        await state.clear()

    # async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    #     await callback.message.edit_text("Выбирайте, <b>Клиент!</b>",
    #                                      reply_markup=keyboards.keyboard_main_student(), parse_mode=ParseMode.HTML)
    #     await callback.answer()
    #     await state.clear()


class ClientManagerTasks:
    None


class ClientManagerEquipment(ClientManager):
    def __init__(self, client: Client):
        super().__init__(client)

    async def show_inventory(self, callback: types.CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id
        details = database.fetchall_multiple("SELECT * FROM details WHERE owner = ?", (user_id,))

        if not details:
            await callback.message.answer(
                StudentMessages.NO_EQUIPMENT_FOUND,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboards.keyboard_alias_back_student()
            )
        else:
            equipment_message = StudentMessages.YOUR_EQUIPMENT_HEADER
            for detail in details:
                detail_id, name, price, owner = detail
                equipment_message += StudentMessages.EQUIPMENT_ITEM_FORMAT.format(
                    detail_id=detail_id, name=name, price=price)
            await callback.message.edit_text(
                equipment_message,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboards.keyboard_alias_back_student()
            )
        await callback.answer()

    # async def back_to_menu(self, callback: types.CallbackQuery, state: FSMContext):
    #     await callback.message.edit_text(
    #         StudentMessages.choose_next_action,
    #         reply_markup=keyboards.keyboard_main_student(),
    #         parse_mode=ParseMode.HTML
    #     )
    #     await callback.answer()
