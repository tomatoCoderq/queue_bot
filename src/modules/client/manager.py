import os
import datetime

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from src.modules.models.operator import Operator
from src.modules.client import keyboard as client_keyboard
from src.modules.tasks import keyboard as tasks_keyboard
from src.modules.operator import keyboard as operator_keyboard
from aiogram import Bot, types
from loguru import logger

from src.storages.excel_writer import create_idt_name_map
from src.storages.files import delete_file
from src.modules.shared.messages import StudentMessages
from sqlalchemy import delete, insert, select, update

from src.storages.sql.dependencies import database
from src.storages.sql.models import (
    DetailModel,
    RequestModel,
    details_table,
    requests_queue_table,
    users_table,
)

from src.modules.models.client import Client

from src.fsm_states.client_states import SendPiece, DeleteOwnQueue


class ClientManager:
    def __init__(self, client: Client):
        self.client = client

    def _generate_message_with_details(self, students_messages: list[RequestModel]) -> str:
        message_to_send = [
            (
                f"<b>ID</b>: {request.id}\n"
                f"<b>Файл</b>: {(request.file_name or 'unknown')}.{request.type}\n"
                f"<b>Статус</b>: {Operator.status_int_to_str(request.status or 0)}\n---\n"
            )
            for request in students_messages
        ]

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
            reply_markup=client_keyboard.keyboard_main_student(),
            parse_mode=ParseMode.HTML,
        )
        await state.clear()

    async def initiate_send_piece(self, callback: types.CallbackQuery, state: FSMContext):
        """Start the piece submission process by showing urgency options."""
        await callback.message.edit_text(
            StudentMessages.urgency_selection,
            reply_markup=client_keyboard.keyboard_urgency_student(),
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
        with database.session() as session:
            request_ids = session.scalars(
                select(requests_queue_table.c.id).where(
                    requests_queue_table.c.proceeed.in_([0, 1])
                )
            ).all()
        if request_ids:
            message_id = request_ids[-1]
        else:
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
        with database.session() as session:
            request_ids = session.scalars(
                select(requests_queue_table.c.id).where(
                    requests_queue_table.c.proceeed.in_([0, 1])
                )
            ).all()
        if request_ids:
            message_id = request_ids[-1]
        else:
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

        request_id = database.execute(
            insert(requests_queue_table).values(
                idt=self.client.telegram_id,
                urgency=data["urgency"],
                type=file_type,
                status=0,
                send_date=now_str,
                comment=data["text"],
                amount=data["amount"],
                file_name=data["file_name"],
                value=value,
                proceeed=0,
            )
        )
        logger.success(f"Added request from {message.from_user.username} to requests_queue")

        await self.rename_file(data['old_file_name'], message, state)

        if "to_approve_urgency" in data.keys():
            names = create_idt_name_map()
            # idt = database.fetchall("SELECT idt FROM users WHERE proceeed=1 or proceeed=0")
            with database.session() as session:
                teacher_ids = session.scalars(
                    select(users_table.c.idt).where(users_table.c.role == "teacher")
                ).all()
            for teacher in teacher_ids:
                await message.bot.send_message(
                    teacher,
                    f"запрос {request_id} от {names[message.from_user.id][0]} {names[message.from_user.id][1]}",
                    reply_markup=tasks_keyboard.keyboard_process_high_urgency_teacher()
                )

        await message.reply(
            StudentMessages.request_queued.format(request_id=request_id),
            parse_mode=ParseMode.HTML,
            reply_markup=client_keyboard.keyboard_main_student()
        )

        await state.clear()

    async def process_high_urgency_decision(self, callback: types.CallbackQuery):
        if callback.data == "confirm_high_urgency":
            id_to_change = int(callback.message.text.split()[1])
            database.execute(
                update(requests_queue_table)
                .where(requests_queue_table.c.id == id_to_change)
                .values(urgency=1)
            )
            logger.success("High urgency confirmed; urgency updated.")
            await callback.answer(StudentMessages.HIGH_URGENCY_ACCEPTED)
            await callback.message.delete()
        else:
            await callback.answer(StudentMessages.HIGH_URGENCY_REJECTED)
            await callback.message.delete()

    async def student_requests(self, callback: types.CallbackQuery, state: FSMContext):
        students_messages = database.fetch_all(
            select(requests_queue_table)
            .where(requests_queue_table.c.proceeed.notin_([2, 4]))
            .where(requests_queue_table.c.idt == callback.from_user.id),
            model=RequestModel,
        )

        await callback.message.edit_text(self._generate_message_with_details(students_messages),
                                         reply_markup=client_keyboard.keyboard_back_to_main_student(),
                                         parse_mode=ParseMode.HTML)
        await callback.answer()
        await state.set_state(DeleteOwnQueue.get_id_to_delete)
        await state.update_data(msg_id=callback.message.message_id)

    async def get_id_to_delete(self, message: types.Message, state: FSMContext, bot: Bot):
        with database.session() as session:
            messages_ids = set(
                session.scalars(
                    select(requests_queue_table.c.id).where(requests_queue_table.c.proceeed == 0)
                ).all()
            )
        data = await state.get_data()

        if not message.text.isdigit() or int(message.text) not in messages_ids:
            await message.reply(StudentMessages.NO_ID_FOUND, parse_mode=ParseMode.HTML)
            logger.error(f"Wrong id was written by {message.from_user.username}")
            return self.get_id_to_delete

        await bot.delete_message(message.chat.id, data['msg_id'])
        # await message.delete()
        delete_file({"id": int(message.text)})
        database.execute(
            update(requests_queue_table)
            .where(requests_queue_table.c.id == int(message.text))
            .values(proceeed=2)
        )
        await message.answer(StudentMessages.SUCESSFULLY_DELETED, reply_markup=client_keyboard.keyboard_main_student())
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
        details = database.fetch_all(
            select(details_table).where(details_table.c.owner == user_id),
            model=DetailModel,
        )

        if not details:
            await callback.message.answer(
                StudentMessages.NO_EQUIPMENT_FOUND,
                parse_mode=ParseMode.HTML,
                reply_markup=client_keyboard.keyboard_alias_back_student()
            )
        else:
            equipment_message = StudentMessages.YOUR_EQUIPMENT_HEADER
            for detail in details:
                equipment_message += StudentMessages.EQUIPMENT_ITEM_FORMAT.format(
                    detail_id=detail.id, name=detail.name, price=detail.price)
            await callback.message.edit_text(
                equipment_message,
                parse_mode=ParseMode.HTML,
                reply_markup=client_keyboard.keyboard_alias_back_student()
            )
        await callback.answer()

    # async def back_to_menu(self, callback: types.CallbackQuery, state: FSMContext):
    #     await callback.message.edit_text(
    #         StudentMessages.choose_next_action,
    #         reply_markup=keyboards.keyboard_main_student(),
    #         parse_mode=ParseMode.HTML
    #     )
    #     await callback.answer()
