import datetime
import os
import random
from typing import List, Union

import aiogram.exceptions
from aiogram import Bot, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from loguru import logger

from src.modules.operator import keyboard as operator_keyboard
from src.modules.tasks import keyboard as tasks_keyboard
from src.modules.client import keyboard as client_keyboard
from src.fsm_states.operator_states import (
    AliasLookupState,
    CheckMessage,
    InventoryAddState,
    ItemActionState,
    ReturnToQueue,
    ShowClientCard,
    ShowClientPenaltyCard,
)
from src.modules.operator.handlers.tasks_queue import map_names_and_idt
from src.modules.shared.messages import StudentMessages, TeacherMessages
from src.modules.models.base_user import BaseUser
from src.modules.models.client import Client
from src.modules.models.operator import Operator
from sqlalchemy import and_, delete, func, insert, select, update

from src.storages.sql.dependencies import database
from src.storages.sql.models import (
    DetailAliasModel,
    DetailModel,
    PenaltyModel,
    RequestModel,
    StudentModel,
    TaskModel,
    detail_aliases_table,
    details_table,
    penalty_table,
    requests_queue_table,
    students_table,
    tasks_table,
)
from src.storages.excel_writer import Excel
from src.storages.files import move_file


class Detail:
    def __init__(self, name: str, price: float, detail_id: int = random.randint(1000, 9999)):
        self.name = name
        self.price = price
        self.detail_id: int = detail_id

    def __str__(self):
        return f"{self.detail_id} {self.name} {self.price}"

    def change_price(self, price: float):
        self.price = price

    def change_name(self, name: str):
        self.name = name

    def get_id(self) -> int:
        return self.detail_id

    @staticmethod
    def detail_exists(detail_id: int) -> bool:
        """Check if a detail with the given ID exists in the details table."""
        result = database.fetch_one(
            select(details_table).where(details_table.c.id == detail_id),
            model=DetailModel,
        )
        return result is not None


class Bucket:
    def __init__(self):
        self.__bucket_array: List[Detail] = list()

    def add_detail(self, detail: Detail):
        self.__bucket_array.append(detail)

    def remove_detail(self, detail_id: int):
        for detail in self.__bucket_array:
            if detail.get_id() == detail_id:
                self.__bucket_array.remove(detail)

    def get_details(self):
        return self.__bucket_array


class OperatorDetails(Operator):
    def __init__(self, telegram_id: str):
        super().__init__(telegram_id)
        self.bucket = Bucket()

    @staticmethod
    def __generate_alias(name: str) -> str:
        vowels = "aeiouAEIOU"
        words = name.split()
        if len(words) >= 2:
            # Take first 3 letters of the first word.
            first_part = words[0][:3].upper() if len(words[0]) >= 3 else words[0].upper()
            # For the second word, take the first letter plus the first non-vowel after it.
            second_word = words[1]
            second_part = second_word[0].upper()
            for ch in second_word[1:]:
                if ch not in vowels:
                    second_part += ch.upper()
                    break
            return first_part + second_part
        else:
            # For a single-word name, simply take the first 5 characters.
            return name[:5].upper()

    def __form_message_with_details(self):
        details_list = self.get_all_details()
        formed_string = ""
        for detail in details_list:
            # Placeholder for further grouping or formatting.
            pass

    @staticmethod
    def add_details_to_bucket(detail: Detail):
        alias = OperatorDetails.__generate_alias(detail.name)

        existing = database.fetch_one(
            select(detail_aliases_table).where(detail_aliases_table.c.name == detail.name),
            model=DetailAliasModel,
        )
        if not existing:
            database.execute(
                insert(detail_aliases_table).values(name=detail.name, alias=alias)
            )

        database.execute(
            insert(details_table).values(name=detail.name, price=detail.price, owner=None)
        )

    def remove_details_from_bucket(self, detail_id: str):
        database.execute(
            delete(details_table).where(details_table.c.id == detail_id)
        )

    def get_all_details(self) -> List[Detail]:
        details = database.fetch_all(
            select(details_table),
            model=DetailModel,
        )
        details_list: List[Detail] = []
        for record in details:
            details_list.append(
                Detail(
                    name=record.name,
                    price=record.price,
                    detail_id=record.id,
                )
            )
        return details_list

    def move_detail_to_client(self, detail_id: str, client_telegram_id: str):
        database.execute(
            update(details_table)
            .where(details_table.c.id == detail_id)
            .values(owner=client_telegram_id)
        )

    def take_detail_from_client(self, detail_id: str):
        database.execute(
            update(details_table)
            .where(details_table.c.id == detail_id)
            .values(owner=None)
        )


class OperatorManager:
    def __init__(self, operator: Operator):
        self.operator = operator

    @staticmethod
    def __form_the_message_with_penalties():
        message_to_send = TeacherMessages.ENTER_USER_ID
        names_ids = map_names_and_idt()

        for idt, name in names_ids.items():
            penalty_count = database.fetch_column(
                select(func.count(penalty_table.c.id)).where(penalty_table.c.idt == str(idt))
            )
            count = penalty_count[-1] if penalty_count else 0
            message_to_send += f"{name[0]} {name[1]} | {idt} | {count}\n"

        return message_to_send

    async def all_users_penalties_show(self, callback_message: Union[types.Message, types.CallbackQuery],
                                       state: FSMContext):
        if isinstance(callback_message, types.Message):
            await callback_message.answer(self.__form_the_message_with_penalties(),
                                          reply_markup=operator_keyboard.keyboard_back_to_main_teacher())
            await state.update_data(prev_msg_id=callback_message.message_id)

        if isinstance(callback_message, types.CallbackQuery):
            await callback_message.message.edit_text(self.__form_the_message_with_penalties(),
                                                     reply_markup=operator_keyboard.keyboard_back_to_main_teacher())
            await state.update_data(prev_msg_id=callback_message.message.message_id)

        await state.set_state(ShowClientCard.get_client_id)


class OperatorManagerDetails(OperatorManager):
    def __init__(self, operator: Operator):
        super().__init__(operator)

    async def cancel_process(self, message: types.Message, state: FSMContext):
        """Cancel current operation and return to the main teacher menu."""
        await self.operator.send_message(
            self.operator.telegram_id,
            bot=message.bot,
            text=TeacherMessages.CANCEL_PROCESS,
            reply_markup=operator_keyboard.keyboard_main_teacher(),
            parse_mode=ParseMode.HTML,
        )
        await state.clear()

    async def show_details_queue(self, callback: types.CallbackQuery):
        """Show the details queue using the dedicated teacher keyboard."""
        await self.operator.edit_message(bot=callback.bot,
                                         text="Действия:",
                                         message_id=callback.message.message_id,
                                         reply_markup=operator_keyboard.keyboard_details_teacher())

    @staticmethod
    def generate_message_to_send(header: str, students_messages: List[RequestModel]) -> str:
        """Build the message containing request details for teacher review."""
        try:
            cidt_name_map = Operator.get_idt_name_map()
        except Exception as e:
            logger.error(f"Error generating ID mapping: {e}")
            return "<b>Ошибка!</b>"
        response = []
        for msg in students_messages:
            response.append(
                f"<b>ID</b>: {msg.id} | {cidt_name_map.get(msg.idt, ('Неизвестно', ''))[0]} "
                f"{cidt_name_map.get(msg.idt, ('', ''))[1]} | {(msg.file_name or 'файл')}.<i>{msg.type}</i>\n"
                f"<b>Количество</b>: {msg.amount or '-'} | <b>Срочность</b>: {Operator.urgency_int_to_str(msg.urgency)} | "
                f"<b>Статус</b>: {Operator.status_int_to_str(msg.status)}\n---\n"
            )
        if not response:
            return header + TeacherMessages.NO_REQUESTS
        return header + "".join(response)

    async def check_messages(self, callback: types.CallbackQuery, state: FSMContext, bot: Bot):
        sort_key = callback.data.replace("sort_", "") if callback.data.startswith("sort_") else None

        students_messages = database.fetch_all(
            select(requests_queue_table).where(requests_queue_table.c.proceeed.in_([0, 1])),
            model=RequestModel,
        )

        # Sort based on the selected key
        if sort_key == "type":
            students_messages.sort(key=lambda x: x.type or "")
        elif sort_key == "date":
            students_messages.sort(key=lambda x: x.send_date or "")
        elif sort_key == "urgency":
            students_messages.sort(key=lambda x: x.urgency, reverse=True)

        s = self.generate_message_to_send(TeacherMessages.SELECT_REQUEST, students_messages)
        # print(s)
        try:
            if callback.data == "check":
                if len(s) > 4096:
                    for x in range(0, len(s), 4096):
                        msg = await callback.message.answer(s[x:x + 4096], parse_mode=ParseMode.HTML)
                    msg = await callback.message.answer("Выбирайте:", reply_markup=operator_keyboard.keyboard_sort_teacher())
                else:
                    msg = await callback.message.edit_text(
                        s, reply_markup=operator_keyboard.keyboard_sort_teacher(), parse_mode=ParseMode.HTML
                    )
            elif callback.data == "back_to_queue":
                await callback.message.delete()
                msg = await callback.message.answer(
                    s, reply_markup=operator_keyboard.keyboard_sort_teacher(), parse_mode=ParseMode.HTML
                )
            else:
                # await callback.message.delete()
                msg = await callback.message.edit_text(
                    s, reply_markup=operator_keyboard.keyboard_sort_teacher(), parse_mode=ParseMode.HTML
                )
        except aiogram.exceptions.TelegramBadRequest as e:
            logger.error(f"Error in check_messages: {e}")
        await state.set_state(CheckMessage.waiting_id)
        await state.update_data(msg=msg.message_id)
        await callback.answer()

    async def handle_waiting_id(self, message: types.Message, state: FSMContext, bot: Bot):
        """
        Process teacher input containing a request ID.
        Deletes the previous message, retrieves detailed info,
        and displays the request file with appropriate action keyboard.
        """
        messages_students = database.fetch_all(
            select(requests_queue_table).where(requests_queue_table.c.proceeed.in_([0, 1])),
            model=RequestModel,
        )
        requests_by_id = {record.id: record for record in messages_students}

        if not message.text.isdigit() or int(message.text) not in requests_by_id:
            await message.reply(TeacherMessages.NO_ID_FOUND, parse_mode=ParseMode.HTML)
            logger.error(f"Wrong ID by {message.from_user.username}")
            return

        selected_request = requests_by_id[int(message.text)]
        spdict = {record.id: record.idt for record in messages_students}
        data = await state.get_data()

        try:
            await bot.delete_message(message.from_user.id, data['msg'])
            # await message.delete()
        except Exception as e:
            await message.answer(TeacherMessages.ID_ERROR)
            logger.error(f"Error deleting messages: {e}")

        cidt_name_map = Operator.get_idt_name_map()
        message_to_send = ""
        message_to_send = (
            f"<b>ID</b>: {selected_request.id}\n"
            f"<b>Имя</b>: {cidt_name_map.get(selected_request.idt, ('Неизвестно', ''))[0]} "
            f"{cidt_name_map.get(selected_request.idt, ('', ''))[1]}\n"
            f"<b>Срочность</b>: {Operator.urgency_int_to_str(selected_request.urgency or 0)}\n"
            f"<b>Тип</b>: {selected_request.type}\n"
            f"<b>Дата отправки</b>: {selected_request.send_date}\n"
            f"<b>Комментарий</b>: {selected_request.comment or '-'}\n"
            f"<b>Количество</b>: {selected_request.amount or '-'}\n"
            f"<b>Вес/Площадь</b>: {selected_request.value or '-'}\n"
        )
        await state.update_data(id=selected_request.id, idt=selected_request.idt, type=selected_request.type)
        file_name = [
            entry for entry in os.listdir(f'students_files/{spdict[int(message.text)]}')
            if entry.startswith(message.text)
        ]
        is_proceed = selected_request.proceeed or 0
        if is_proceed == 0:
            msg_obj = await message.answer_document(
                document=types.FSInputFile(f"students_files/{spdict[int(message.text)]}/{file_name[0]}"),
                caption=message_to_send,
                reply_markup=operator_keyboard.keyboard_teacher_actions_one(),
                parse_mode=ParseMode.HTML,
            )
        elif is_proceed == 1:
            msg_obj = await message.answer_document(
                document=types.FSInputFile(f"students_files/{spdict[int(message.text)]}/{file_name[0]}"),
                caption=message_to_send,
                reply_markup=operator_keyboard.keyboard_teacher_actions_two(),
                parse_mode=ParseMode.HTML,
            )
        await state.set_state(CheckMessage.waiting_action)
        # await state.update_data(msg=msg_obj.message_id)
        # logger.info(f"Set waiting_action with msg id {msg_obj.message_id}")

    async def accept_task(self, callback: types.CallbackQuery, bot: Bot, state: FSMContext):
        """Accept a task by updating its status and notifying the client."""
        data = await state.get_data()
        print(data['idt'])
        with database.session() as session:
            messages_ids = set(
                session.scalars(
                    select(requests_queue_table.c.id).where(requests_queue_table.c.proceeed == 0)
                ).all()
            )
        if data['id'] in messages_ids:
            database.execute(
                update(requests_queue_table)
                .where(requests_queue_table.c.id == data['id'])
                .values(proceeed=1)
            )
            logger.success("Task accepted")
            await self.operator.send_message(data['idt'], bot, TeacherMessages.REQUEST_ACCEPTED.format(id=data['id']))
            await callback.answer("Принято в работу", reply_markup=operator_keyboard.keyboard_main_teacher())
        else:
            logger.error("Task already taken")
            await callback.answer(TeacherMessages.REQUEST_ALREADY_IN_WORK,
                                  reply_markup=operator_keyboard.keyboard_main_teacher())

    async def reject_task(self, callback: types.CallbackQuery, bot: Bot, state: FSMContext):
        """Reject a task by updating its status and notifying the client."""
        data = await state.get_data()
        with database.session() as session:
            messages_ids = set(
                session.scalars(
                    select(requests_queue_table.c.id).where(requests_queue_table.c.proceeed == 0)
                ).all()
            )
        if data['id'] in messages_ids:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            database.execute(
                update(requests_queue_table)
                .where(requests_queue_table.c.id == data['id'])
                .values(proceeed=4, close_time=current_time)
            )
            logger.success("Task rejected")
            await self.operator.send_message(bot, TeacherMessages.REQUEST_REJECTED.format(id=data['id']))
            await callback.answer("Отклонено", reply_markup=operator_keyboard.keyboard_main_teacher())
            await callback.message.delete()
            await callback.message.answer(TeacherMessages.CHOOSE_MAIN_TEACHER,
                                          reply_markup=operator_keyboard.keyboard_main_teacher())
        else:
            logger.error("Task already taken")
            await callback.answer(TeacherMessages.REQUEST_ALREADY_IN_WORK,
                                  reply_markup=operator_keyboard.keyboard_main_teacher())

    async def finish_work(self, callback: types.CallbackQuery, state: FSMContext):
        """Handle finishing of a task; request additional parameters based on task type."""
        data = await state.get_data()
        request = database.fetch_one(
            select(requests_queue_table).where(requests_queue_table.c.id == data['id']),
            model=RequestModel,
        )
        if not request:
            await callback.answer(TeacherMessages.NO_ID_FOUND)
            return

        if (request.proceeed or 0) == 0:
            await callback.answer(TeacherMessages.REQUEST_NOT_IN_WORK)
            return
        elif request.proceeed == 1:
            await callback.message.delete()
            if data['type'] == "stl":
                msg_obj = await callback.message.answer(TeacherMessages.SEND_WEIGHT_REPORT, parse_mode=ParseMode.HTML)
            elif data['type'] == "dxf":
                msg_obj = await callback.message.answer(TeacherMessages.SEND_SIZE_REPORT, parse_mode=ParseMode.HTML)
            await state.set_state(CheckMessage.waiting_size)
            await callback.answer()
            await state.update_data(msg=msg_obj.message_id)
            logger.info(f"Set waiting_size with msg id {msg_obj.message_id}")

    async def finish_work_get_params(self, message: types.Message, state: FSMContext):
        """Receive additional parameters (e.g., size or weight) and update the task."""
        data = await state.get_data()

        if message.text == "0":
            await message.answer(TeacherMessages.SEND_PHOTO_REPORT)
            await state.set_state(CheckMessage.waiting_photo_report)
        else:
            if data['type'] == "stl" and not message.text.isdigit():
                await message.answer(StudentMessages.INVALID_AMOUNT_INPUT)
                return
            if data['type'] == "dxf":
                parts = message.text.split()
                if len(parts) != 2 or not (parts[0].isdigit() and parts[1].isdigit()):
                    await message.answer(TeacherMessages.INVALID_SIZE_INPUT)
                    return

            to_set = message.text if data['type'] == "stl" else int(parts[0]) * int(parts[1])
            database.execute(
                update(requests_queue_table)
                .where(requests_queue_table.c.id == data['id'])
                .values(params=to_set)
            )

            await message.answer(TeacherMessages.SEND_PHOTO_REPORT)
            await state.set_state(CheckMessage.waiting_photo_report)

    async def finish_work_report(self, message: types.Message, bot: Bot, state: FSMContext):
        """Finalize the task by generating an Excel report, moving files, and notifying the client."""
        data = await state.get_data()

        excel_table = Excel()
        await bot.delete_message(message.from_user.id, int(data['msg']))

        excel_table.write(
            database.fetchall_multiple(
                select(requests_queue_table).where(requests_queue_table.c.id == data['id'])
            )
        )
        move_file(data)

        database.execute(
            update(requests_queue_table)
            .where(requests_queue_table.c.id == data['id'])
            .values(proceeed=2)
        )
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name = f"temporal/{data['idt']}{current_time}.jpg"
        open(file_name, "w").close()
        await bot.download(message.photo[-1], file_name)

        await bot.send_photo(
            data['idt'],
            photo=types.FSInputFile(file_name),
            caption=f"Ваша работа с ID {data['id']} завершена!"
        )

        try:
            os.remove(file_name)
        except OSError as e:
            logger.error(f"Error removing temporary file: {e}")
        await self.operator.send_message(
            self.operator.telegram_id,
            bot,
            TeacherMessages.PHOTO_SENT_TO_STUDENT,
            reply_markup=operator_keyboard.keyboard_main_teacher(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()
        logger.success("Finished work report, state cleared.")

    async def get_xlsx(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await callback.message.answer_document(document=FSInputFile(os.getenv("FILE")),
                                               reply_markup=operator_keyboard.keyboard_back_to_details_teacher())

    async def history(self, callback: types.CallbackQuery, state: FSMContext):
        students_messages = database.fetch_all(
            select(requests_queue_table)
            .where(requests_queue_table.c.proceeed == 4)
            .order_by(requests_queue_table.c.close_time.desc())
            .limit(3),
            model=RequestModel,
        )

        message_to_send = OperatorManagerDetails.generate_message_to_send(
            "Напишите ID, чтобы вернуть его из удаленных\n",
            students_messages)

        await callback.message.edit_text(message_to_send, reply_markup=operator_keyboard.keyboard_back_to_details_teacher())
        await callback.answer()

        await state.set_state(ReturnToQueue.waiting_id)
        await state.update_data(msg_id=callback.message.message_id)

    async def return_detail_to_queue(self, message: types.Message, state: FSMContext, bot: Bot):
        with database.session() as session:
            messages_ids = set(
                session.scalars(
                    select(requests_queue_table.c.id)
                    .where(requests_queue_table.c.proceeed == 4)
                    .order_by(requests_queue_table.c.close_time.desc())
                    .limit(3)
                ).all()
            )
        data = await state.get_data()

        if not message.text.isdigit() or int(message.text) not in messages_ids:
            await message.reply(TeacherMessages.NO_ID_FOUND)
            logger.error(f"Wrong id was written by {message.from_user.username}")
            return self.return_to_queue

        database.execute(
            update(requests_queue_table)
            .where(requests_queue_table.c.id == int(message.text))
            .values(proceeed=0)
        )

        await message.delete()
        await bot.delete_message(message.from_user.id, data['msg_id'])

        await message.answer("Сделано " + TeacherMessages.CHOOSE_MAIN_TEACHER,
                             reply_markup=operator_keyboard.keyboard_main_teacher())

        await state.clear()

    async def process_high_urgency(self, callback: types.CallbackQuery) -> None:

        if callback.data == CallbackDataKeys.confirm_high_urgency:
            id_to_change = int(callback.message.text.split()[1])

            database.execute(
                update(requests_queue_table)
                .where(requests_queue_table.c.id == id_to_change)
                .values(urgency=1)
            )
            logger.success("UPDATED urgency=3 after confirm by Operator")

            await callback.answer(StudentMessages.HIGH_URGENCY_ACCEPTED)
            await callback.message.delete()

        else:
            await callback.answer(StudentMessages.HIGH_URGENCY_REJECTED)
            await callback.message.delete()

class OperatorManagerPenalties(OperatorManager):
    def __init__(self, operator: Operator):
        super().__init__(operator)

    # async def penalty_card(self, message, state, bot, idt):
    #     client = Client(idt, "qw")
    #
    #     penalties = client.get_penalties()
    #
    #     message_to_send = "<b>ID | Причина</b>\n"
    #     message_to_send += penalties
    #
    #     await message.delete()
    #
    #     await message.answer(message_to_send, reply_markup=keyboards.keyboard_penalty_card_teacher())
    #
    #     await state.update_data(prev_msg_id=message.message_id)
    #     await state.set_state(ShowClientPenaltyCard.further_actions)
    #
    # # async def penalty(callback: types.CallbackQuery, state: FSMContext):
    # #     await all_users_penalties_show(callback, state)
    #
    # async def show_penalty_card(self, message: types.Message, state: FSMContext, bot: Bot):
    #     data = await state.get_data()
    #     await bot.delete_message(message.from_user.id, data['prev_msg_id'])
    #     await self.penalty_card(message, state, bot, message.text)
    #     await state.update_data(idt=message.text)
    #
    # async def add_penalty(self, callback: types.CallbackQuery, state: FSMContext):
    #     await callback.message.edit_text(TeacherMessages.ENTER_PENALTY_REASON)
    #     await state.set_state(ShowClientPenaltyCard.get_penalty_reasons)
    #
    # async def insert_added_penalty(self, message: types.Message, state: FSMContext, bot: Bot):
    #     data = await state.get_data()
    #     reasons = message.text
    #     to_add = [data['idt'], reasons]
    #     database.execute("Insert into penalty values (NULL, ?, ? )", to_add)
    #     await message.answer(TeacherMessages.PENALTY_ADDED)
    #     await self.penalty_card(message, state, bot, data['idt'])
    #
    # async def remove_penalty(self, callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    #     await callback.message.answer(TeacherMessages.ENTER_PENALTY_ID_TO_DELETE)
    #     await state.update_data(msg_to_delete=[callback.message.message_id])
    #     await state.set_state(ShowClientPenaltyCard.get_penalty_id_to_delete)
    #
    # async def delete_removed_penalty(self, message: types.Message, state: FSMContext, bot: Bot):
    #     data = await state.get_data()
    #
    #     if not message.text.isdigit():
    #         await message.answer(TeacherMessages.ONLY_NUMBERS_ALLOWED)
    #         return self.delete_removed_penalty
    #
    #     database.execute("delete from penalty where id=?", (message.text,))
    #
    #     for msg in data['msg_to_delete']:
    #         await bot.delete_message(message.from_user.id, msg)
    #
    #     await message.answer(TeacherMessages.PENALTY_DELETED)
    #     await self.penalty_card(message, state, bot, data['idt'])
    #
    # async def back_to_penalties_teacher(self, callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    #     await self.all_users_penalties_show(callback, state)


class OperatorManagerStudentCards(OperatorManager):
    def __init__(self, operator: Operator):
        super().__init__(operator)

    async def show_client_card(self, callback: types.CallbackQuery, state: FSMContext):
        idt = int(callback.data.split("_")[-1])

        message_id = callback.message.message_id

        client = Client(idt)

        client_card = client.full_card()

        await callback.message.delete()

        await callback.message.answer(client_card, reply_markup=operator_keyboard.keyboard_student_card_actions())

        await state.update_data(idt=idt)
        await state.update_data(prev_msg_id=message_id)
        await state.set_state(ShowClientCard.further_actions)

    async def change_task(self, message: types.Message, state: FSMContext, task_number: int):
        data = await state.get_data()
        task_field = "task_first" if task_number == 1 else "task_second"
        task_id = database.last_added_id(data["idt"])

        target_column = tasks_table.c.task_first if task_number == 1 else tasks_table.c.task_second
        database.execute(
            update(tasks_table)
            .where(tasks_table.c.id == task_id)
            .where(tasks_table.c.status.in_([1, 5]))
            .values({target_column.name: message.text})
        )

        await message.answer(f"✅ Задание {task_number} изменено", reply_markup=operator_keyboard.keyboard_main_teacher())
        await message.bot.send_message(data["idt"], f"🛠 Задание {task_number} обновлено оператором")
        await state.clear()

    async def set_all_tasks(self, message: types.Message, state: FSMContext, task_one: str, task_two: str):
        data = await state.get_data()
        now = datetime.datetime.now(datetime.timezone.utc)

        database.execute(
            insert(tasks_table).values(
                idt=int(data["idt"]),
                task_first=task_one,
                task_second=task_two,
                start_time=now.strftime("%Y-%m-%d %H:%M:%S"),
                status=1,
                shift=0,
            )
        )

        request_id = database.last_added_id(int(data['idt']))

        await message.answer(StudentMessages.SUCESSFULLY_ADDED_TASKS.format(request_id=request_id),
                             reply_markup=operator_keyboard.keyboard_main_teacher())
        await state.clear()

    async def add_penalty(self, callback: types.CallbackQuery, state: FSMContext, reason):
        data = await state.get_data()
        client = Client(data['idt'])

        database.execute(
            insert(penalty_table).values(
                idt=data["idt"],
                reason=client.penalties_reason_map[reason],
            )
        )

        client_card = client.full_card()

        # await message.delete()
        await callback.message.edit_text("✅ Штраф добавлен\n\n" + client_card, reply_markup=operator_keyboard.keyboard_student_card_actions())
        await callback.bot.send_message(client.telegram_id, f"⚠️ Вам назначен штраф: <b>{client.penalties_reason_map[reason]}</b>.")

        await state.set_state(ShowClientCard.further_actions)

    async def add_penalty_with_photo(self, message: types.Message, state: FSMContext, reason, photo):
        data = await state.get_data()
        client = Client(data['idt'])

        database.execute(
            insert(penalty_table).values(
                idt=data["idt"],
                reason=client.penalties_reason_map[reason],
            )
        )

        client_card = client.full_card()

        await message.answer("✅ Штраф добавлен\n\n" + client_card, reply_markup=operator_keyboard.keyboard_student_card_actions())
        await message.bot.send_photo(client.telegram_id, caption=f"⚠️ Вам назначен штраф: <b>{client.penalties_reason_map[reason]}</b>.", photo=photo)

        await state.set_state(ShowClientCard.further_actions)

    async def remove_penalty(self, message: types.Message, penalty_id: int, state: FSMContext):
        data = await state.get_data()

        # Verify that the penalty exists and belongs to the current client
        existing_penalty = database.fetch_one(
            select(penalty_table)
            .where(penalty_table.c.id == penalty_id)
            .where(penalty_table.c.idt == data["idt"]),
            model=PenaltyModel,
        )

        if not existing_penalty:
            await message.answer("❌ Штраф с таким ID не найден у этого пользователя.")
            return

        # Proceed with deletion if valid
        database.execute(
            delete(penalty_table).where(penalty_table.c.id == penalty_id)
        )

        client = Client(data['idt'])
        client_card = client.full_card()

        await message.bot.delete_message(message.from_user.id, data["msg_id"])
        await message.delete()
        await message.answer("✅ Штраф удалён\n\n" + client_card, reply_markup=operator_keyboard.keyboard_student_card_actions())

        await state.set_state(ShowClientCard.further_actions)


class OperatorManagerEquipment(OperatorManager):
    def __init__(self, operator: Operator):
        super().__init__(operator)

    async def form_message_with_bucket(self, callback: Union[types.CallbackQuery, types.Message], state: FSMContext):
        operator = OperatorDetails(str(callback.from_user.id))
        details_list = operator.get_all_details()

        detail_groups = {}
        for detail in details_list:
            detail_groups.setdefault(detail.name, []).append(detail)

        summary_lines = []
        for name, items in detail_groups.items():
            alias_record = database.fetch_one(
                select(detail_aliases_table).where(detail_aliases_table.c.name == name),
                model=DetailAliasModel,
            )
            alias = alias_record.alias if alias_record else name[:5].upper()
            summary_lines.append(f"🔸 <b>{alias}</b> (<i>{name}</i>): <b>{len(items)}</b> шт.")
        summary = "\n".join(summary_lines) if summary_lines else "<b>Нет деталей в инвентаре.</b>"

        if isinstance(callback, types.CallbackQuery):
            await callback.message.edit_text(summary, parse_mode=ParseMode.HTML,
                                             reply_markup=operator_keyboard.keyboard_inventory())
        else:
            await callback.answer(summary, parse_mode=ParseMode.HTML, reply_markup=operator_keyboard.keyboard_inventory())

    async def show_bucket(self, callback: types.CallbackQuery, state: FSMContext):
        await self.form_message_with_bucket(callback, state)

        await state.set_state(AliasLookupState.waiting_for_alias)

    async def inventory_add_start(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "<b>Введите название детали</b> и <b>цену</b> через запятую.\nПример: <i>Arduino Mega, 1500</i>",
            reply_markup=operator_keyboard.keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(InventoryAddState.waiting_for_detail_info)

    async def process_inventory_add(self, message: types.Message, state: FSMContext):
        text = message.text
        try:
            # Expect input format: "Название, цена"
            name, price_str = [part.strip() for part in text.split(",", 1)]
            price = float(price_str)
        except Exception as e:
            await message.answer(
                "<b>Неверный формат!</b> Введите данные в формате: <i>Название, цена</i>",
                parse_mode=ParseMode.HTML
            )
            return

        new_detail = Detail(name=name, price=price)
        OperatorDetails.add_details_to_bucket(detail=new_detail)

        await message.answer(
            f"✅ Деталь «<b>{name}</b>» успешно добавлена со стоимостью <b>{price}</b>.",
            reply_markup=operator_keyboard.keyboard_inventory(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()

    async def process_alias_lookup(self, message: types.Message, state: FSMContext):
        user_alias = message.text.strip().upper()

        alias_lookup = database.fetch_one(
            select(detail_aliases_table).where(detail_aliases_table.c.alias == user_alias),
            model=DetailAliasModel,
        )
        if not alias_lookup:
            await message.answer(
                "❌ <b>Ошибка:</b> Объект с алиасом <i>{}</i> не найден.".format(user_alias),
                reply_markup=operator_keyboard.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        full_name = alias_lookup.name

        details = database.fetch_all(
            select(details_table).where(details_table.c.name == full_name),
            model=DetailModel,
        )
        if not details:
            await message.answer(
                "❌ <b>Ошибка:</b> Нет деталей с именем <i>{}</i> в инвентаре.".format(full_name),
                reply_markup=operator_keyboard.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        # output = await form_message_detail_info(message, state, details)

        cost = details[0].price
        owner_name_map = Operator.get_idt_name_map()

        output_lines = [f"💰 <b>Цена:</b> {cost}", "📦 <b>Объекты:</b>"]
        for detail in details:
            obj_id = detail.id
            owner_id = detail.owner
            if owner_id and owner_id in owner_name_map:
                owner_name = f"{owner_name_map[owner_id][0]} {owner_name_map[owner_id][1]}"
            else:
                owner_name = "Нет владельца"
            output_lines.append(f"🔹 <b>ID:</b> {obj_id} | <b>Владелец:</b> {owner_name}")

        output = "\n".join(output_lines)

        await message.answer(output, reply_markup=operator_keyboard.keyboard_transfer_return(), parse_mode=ParseMode.HTML)
        await state.clear()

    async def transfer_item(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "Введите <b>ID объекта</b> и <b>ID нового владельца</b> через запятую.\nПример: <i>23, 987654321</i>",
            reply_markup=operator_keyboard.keyboard_alias_back(),
            parse_mode=ParseMode.HTML)
        await state.set_state(ItemActionState.waiting_for_transfer_info)

    async def process_transfer_item(self, message: types.Message, state: FSMContext):
        try:
            obj_id_str, new_owner_str = [part.strip() for part in message.text.split(",", 1)]
            obj_id = int(obj_id_str)
            new_owner = int(new_owner_str)
        except ValueError:
            await message.answer(
                "❌ <b>Ошибка:</b> Введите корректные числа в формате: <i>ID объекта, ID нового владельца</i>.",
                reply_markup=operator_keyboard.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        if not Detail.detail_exists(obj_id):
            await message.answer(
                f"❌ <b>Ошибка:</b> Объект с ID <b>{obj_id}</b> не найден в инвентаре.",
                reply_markup=operator_keyboard.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        if not BaseUser.user_exists(new_owner):
            await message.answer(
                f"❌ <b>Ошибка:</b> Пользователь с ID <b>{new_owner}</b> не найден в системе.",
                reply_markup=operator_keyboard.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        database.execute(
            update(details_table)
            .where(details_table.c.id == obj_id)
            .values(owner=new_owner)
        )
        await message.answer(
            f"✅ Объект с ID <b>{obj_id}</b> успешно передан пользователю <b>{new_owner}</b>.",
            reply_markup=operator_keyboard.keyboard_transfer_return(),
            parse_mode=ParseMode.HTML
        )
        # await form_message_with_bucket(message, state)
        await state.set_state(AliasLookupState.waiting_for_alias)

    async def return_item(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "Введите <b>ID объекта</b> для возврата.\nПример: <i>23</i>",
            reply_markup=operator_keyboard.keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(ItemActionState.waiting_for_return_info)

    async def process_return_item(self, message: types.Message, state: FSMContext):
        try:
            obj_id = int(message.text.strip())
        except ValueError:
            await message.answer(
                "❌ <b>Ошибка:</b> Введите корректный числовой ID объекта.",
                reply_markup=operator_keyboard.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        if not Detail.detail_exists(obj_id):
            await message.answer(
                f"❌ <b>Ошибка:</b> Объект с ID <b>{obj_id}</b> не найден в инвентаре.",
                reply_markup=operator_keyboard.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        database.execute(
            update(details_table)
            .where(details_table.c.id == obj_id)
            .values(owner=None)
        )
        await message.answer(
            f"✅ Объект с ID <b>{obj_id}</b> успешно возвращён в инвентарь.",
            reply_markup=operator_keyboard.keyboard_transfer_return(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()

    # async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    #     None
