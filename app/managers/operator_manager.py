import datetime
import random
from datetime import *
from typing import Union, List

import aiogram.exceptions
from aiogram.types import FSInputFile

from app.handlers.teacher_tasks_queue import map_names_and_idt
from app.models.base_user import BaseUser
from app.models.client import Client
from app.utils.messages import TeacherMessages
from app.utils.excel_writer import Excel
from app.models.operator import Operator
from app.utils.files import *

from app.fsm_states.operator_states import CheckMessage, ShowClientPenaltyCard, ReturnToQueue, ShowClientCard, \
    AliasLookupState, InventoryAddState, ItemActionState


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
        result = database.fetchall("SELECT id FROM details WHERE id=?", (detail_id,))
        return bool(result)


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

        existing = database.fetchall("SELECT alias FROM detail_aliases WHERE name=?", (detail.name,))
        if not existing:
            database.execute("INSERT INTO detail_aliases VALUES (?, ?)", (detail.name, alias))

        database.execute("INSERT INTO details VALUES (NULL, ?, ?, NULL)", (detail.name, detail.price))

    def remove_details_from_bucket(self, detail_id: str):
        database.execute("DELETE FROM details WHERE id=?", (detail_id,))

    def get_all_details(self) -> List[Detail]:
        details = database.fetchall_multiple("SELECT * FROM details")
        details_list: List[Detail] = list()
        for detail in details:
            details_list.append(Detail(
                name=detail[1],
                price=detail[2],
                detail_id=detail[0]
            ))
        return details_list

    def move_detail_to_client(self, detail_id: str, client_telegram_id: str):
        database.execute("UPDATE details SET owner=? WHERE id=?", (client_telegram_id, detail_id))

    def take_detail_from_client(self, detail_id: str):
        database.execute("UPDATE details SET owner=NULL WHERE id=?", (detail_id,))


class OperatorManager:
    def __init__(self, operator: Operator):
        self.operator = operator

    @staticmethod
    def __form_the_message_with_penalties():
        message_to_send = TeacherMessages.ENTER_USER_ID
        names_ids = map_names_and_idt()

        for idt, name in names_ids.items():
            number_of_penalties = database.fetchall("Select count(id) from penalty where idt=?", (str(idt),))
            message_to_send += f"{name[0]} {name[1]} | {idt} | {number_of_penalties[-1]}\n"

        return message_to_send

    async def all_users_penalties_show(self, callback_message: Union[types.Message, types.CallbackQuery],
                                       state: FSMContext):
        if isinstance(callback_message, types.Message):
            await callback_message.answer(self.__form_the_message_with_penalties(),
                                          reply_markup=keyboards.keyboard_back_to_main_teacher())
            await state.update_data(prev_msg_id=callback_message.message_id)

        if isinstance(callback_message, types.CallbackQuery):
            await callback_message.message.edit_text(self.__form_the_message_with_penalties(),
                                                     reply_markup=keyboards.keyboard_back_to_main_teacher())
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
            reply_markup=keyboards.keyboard_main_teacher(),
            parse_mode=ParseMode.HTML,
        )
        await state.clear()

    async def show_details_queue(self, callback: types.CallbackQuery):
        """Show the details queue using the dedicated teacher keyboard."""
        await self.operator.edit_message(bot=callback.bot,
                                         text="Действия:",
                                         message_id=callback.message.message_id,
                                         reply_markup=keyboards.keyboard_details_teacher())

    @staticmethod
    def generate_message_to_send(header: str, students_messages) -> str:
        """Build the message containing request details for teacher review."""
        try:
            cidt_name_map = Operator.get_idt_name_map()
        except Exception as e:
            logger.error(f"Error generating ID mapping: {e}")
            return "<b>Ошибка!</b>"
        response = []
        for msg in students_messages:
            # Expected msg indices:
            # 0: request id, 1: student telegram id, 2: urgency, 3: type,
            # 4: status, 5: send date, 6: comment, 7: quantity, 8: file name/info.
            response.append(
                f"<b>ID</b>: {msg[0]} | {cidt_name_map[msg[1]][0]} {cidt_name_map[msg[1]][1]} | {msg[8]}.<i>{msg[3]}</i>\n"
                f"<b>Количество</b>: {msg[7]} | <b>Срочность</b>: {Operator.urgency_int_to_str(msg[2])} | "
                f"<b>Статус</b>: {Operator.status_int_to_str(msg[4])}\n---\n"
            )
        if not response:
            return header + TeacherMessages.NO_REQUESTS
        return header + "".join(response)

    async def check_messages(self, callback: types.CallbackQuery, state: FSMContext, bot: Bot):
        sort_key = callback.data.replace("sort_", "") if callback.data.startswith("sort_") else None

        students_messages = database.fetchall_multiple(
            "SELECT * FROM requests_queue WHERE proceeed=0 OR proceeed=1"
        )

        # Sort based on the selected key
        if sort_key == "type":
            students_messages.sort(key=lambda x: x[3])  # ID is at index 0
        elif sort_key == "date":
            students_messages.sort(key=lambda x: x[5])  # Date is at index 5
        elif sort_key == "urgency":
            students_messages.sort(key=lambda x: x[2], reverse=True)  # Urgency is at index 2

        s = self.generate_message_to_send(TeacherMessages.SELECT_REQUEST, students_messages)
        # print(s)
        try:
            if callback.data == "check":
                if len(s) > 4096:
                    for x in range(0, len(s), 4096):
                        msg = await callback.message.answer(s[x:x + 4096], parse_mode=ParseMode.HTML)
                    msg = await callback.message.answer("Выбирайте:", reply_markup=keyboards.keyboard_sort_teacher())
                else:
                    msg = await callback.message.edit_text(
                        s, reply_markup=keyboards.keyboard_sort_teacher(), parse_mode=ParseMode.HTML
                    )
            elif callback.data == "back_to_queue":
                await callback.message.delete()
                msg = await callback.message.answer(
                    s, reply_markup=keyboards.keyboard_sort_teacher(), parse_mode=ParseMode.HTML
                )
            else:
                # await callback.message.delete()
                msg = await callback.message.edit_text(
                    s, reply_markup=keyboards.keyboard_sort_teacher(), parse_mode=ParseMode.HTML
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
        messages_students = database.fetchall_multiple(
            "SELECT * FROM requests_queue WHERE proceeed=0 OR proceeed=1"
        )
        messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0 or proceeed=1")
        students_ids = database.fetchall("SELECT idt FROM requests_queue WHERE proceeed=0 or proceeed=1")
        if not message.text.isdigit() or int(message.text) not in messages_ids:
            await message.reply(TeacherMessages.NO_ID_FOUND, parse_mode=ParseMode.HTML)
            logger.error(f"Wrong ID by {message.from_user.username}")
            return

        spdict = {messages_ids[i]: students_ids[i] for i in range(len(messages_ids))}
        data = await state.get_data()

        try:
            await bot.delete_message(message.from_user.id, data['msg'])
            # await message.delete()
        except Exception as e:
            await message.answer(TeacherMessages.ID_ERROR)
            logger.error(f"Error deleting messages: {e}")

        cidt_name_map = Operator.get_idt_name_map()
        message_to_send = ""
        for msg in messages_students:
            if msg[0] == int(message.text):
                message_to_send = (
                    f"<b>ID</b>: {msg[0]}\n"
                    f"<b>Имя</b>: {cidt_name_map[msg[1]][0]} {cidt_name_map[msg[1]][1]}\n"
                    f"<b>Срочность</b>: {Operator.urgency_int_to_str(msg[2])}\n"
                    f"<b>Тип</b>: {msg[3]}\n"
                    f"<b>Дата отправки</b>: {msg[5]}\n"
                    f"<b>Комментарий</b>: {msg[6]}\n"
                    f"<b>Количество</b>: {msg[7]}\n"
                    f"<b>Вес/Площадь</b>: {msg[9]}\n"
                )
                await state.update_data(id=msg[0], idt=msg[1], type=msg[3])
                break
        file_name = [
            entry for entry in os.listdir(f'students_files/{spdict[int(message.text)]}')
            if entry.startswith(message.text)
        ]
        is_proceed = database.fetchall("SELECT proceeed FROM requests_queue WHERE id=?", (message.text,))[0]
        if is_proceed == 0:
            msg_obj = await message.answer_document(
                document=types.FSInputFile(f"students_files/{spdict[int(message.text)]}/{file_name[0]}"),
                caption=message_to_send,
                reply_markup=keyboards.keyboard_teacher_actions_one(),
                parse_mode=ParseMode.HTML,
            )
        elif is_proceed == 1:
            msg_obj = await message.answer_document(
                document=types.FSInputFile(f"students_files/{spdict[int(message.text)]}/{file_name[0]}"),
                caption=message_to_send,
                reply_markup=keyboards.keyboard_teacher_actions_two(),
                parse_mode=ParseMode.HTML,
            )
        await state.set_state(CheckMessage.waiting_action)
        # await state.update_data(msg=msg_obj.message_id)
        # logger.info(f"Set waiting_action with msg id {msg_obj.message_id}")

    async def accept_task(self, callback: types.CallbackQuery, bot: Bot, state: FSMContext):
        """Accept a task by updating its status and notifying the client."""
        data = await state.get_data()
        print(data['idt'])
        messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0")
        if data['id'] in messages_ids:
            database.execute("UPDATE requests_queue SET proceeed=1 WHERE id=?", (data['id'],))
            logger.success("Task accepted")
            await self.operator.send_message(data['idt'], bot, TeacherMessages.REQUEST_ACCEPTED.format(id=data['id']))
            await callback.answer("Принято в работу", reply_markup=keyboards.keyboard_main_teacher())
        else:
            logger.error("Task already taken")
            await callback.answer(TeacherMessages.REQUEST_ALREADY_IN_WORK,
                                  reply_markup=keyboards.keyboard_main_teacher())

    async def reject_task(self, callback: types.CallbackQuery, bot: Bot, state: FSMContext):
        """Reject a task by updating its status and notifying the client."""
        data = await state.get_data()
        messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0")
        if data['id'] in messages_ids:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            database.execute("UPDATE requests_queue SET proceeed=4, close_time=? WHERE id=?",
                             (current_time, data['id']))
            logger.success("Task rejected")
            await self.operator.send_message(bot, TeacherMessages.REQUEST_REJECTED.format(id=data['id']))
            await callback.answer("Отклонено", reply_markup=keyboards.keyboard_main_teacher())
            await callback.message.delete()
            await callback.message.answer(TeacherMessages.CHOOSE_MAIN_TEACHER,
                                          reply_markup=keyboards.keyboard_main_teacher())
        else:
            logger.error("Task already taken")
            await callback.answer(TeacherMessages.REQUEST_ALREADY_IN_WORK,
                                  reply_markup=keyboards.keyboard_main_teacher())

    async def finish_work(self, callback: types.CallbackQuery, state: FSMContext):
        """Handle finishing of a task; request additional parameters based on task type."""
        data = await state.get_data()
        is_proceed = database.fetchall("SELECT proceeed FROM requests_queue WHERE id=?", (data['id'],))[0]
        if is_proceed == 0:
            await callback.answer(TeacherMessages.REQUEST_NOT_IN_WORK)
            return
        elif is_proceed == 1:
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
            database.execute("UPDATE requests_queue SET params=? WHERE id=?", (to_set, data['id']))

            await message.answer(TeacherMessages.SEND_PHOTO_REPORT)
            await state.set_state(CheckMessage.waiting_photo_report)

    async def finish_work_report(self, message: types.Message, bot: Bot, state: FSMContext):
        """Finalize the task by generating an Excel report, moving files, and notifying the client."""
        data = await state.get_data()

        excel_table = Excel()
        await bot.delete_message(message.from_user.id, int(data['msg']))

        excel_table.write(database.fetchall_multiple("SELECT * FROM requests_queue WHERE id=?", (data['id'],)))
        move_file(data)

        database.execute("UPDATE requests_queue SET proceeed=2 WHERE id=?", (data['id'],))
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
            reply_markup=keyboards.keyboard_main_teacher(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()
        logger.success("Finished work report, state cleared.")

    async def get_xlsx(self, callback: types.CallbackQuery):
        await callback.message.delete()
        await callback.message.answer_document(document=FSInputFile(os.getenv("FILE")),
                                               reply_markup=keyboards.keyboard_back_to_details_teacher())

    async def history(self, callback: types.CallbackQuery, state: FSMContext):
        students_messages = database.fetchall_multiple("select * from requests_queue where "
                                                       "proceeed=4 order by close_time desc limit 3")

        message_to_send = OperatorManagerDetails.generate_message_to_send(
            "Напишите ID, чтобы вернуть его из удаленных\n",
            students_messages)

        await callback.message.edit_text(message_to_send, reply_markup=keyboards.keyboard_back_to_details_teacher())
        await callback.answer()

        await state.set_state(ReturnToQueue.waiting_id)
        await state.update_data(msg_id=callback.message.message_id)

    async def return_detail_to_queue(self, message: types.Message, state: FSMContext, bot: Bot):
        messages_ids = database.fetchall("select id from requests_queue where "
                                         "proceeed=4 order by close_time desc limit 3")
        data = await state.get_data()

        if not message.text.isdigit() or int(message.text) not in messages_ids:
            await message.reply(TeacherMessages.NO_ID_FOUND)
            logger.error(f"Wrong id was written by {message.from_user.username}")
            return self.return_to_queue

        database.execute("update requests_queue set proceeed=0 where id=?", (int(message.text),))

        await message.delete()
        await bot.delete_message(message.from_user.id, data['msg_id'])

        await message.answer("Сделано " + TeacherMessages.CHOOSE_MAIN_TEACHER,
                             reply_markup=keyboards.keyboard_main_teacher())

        await state.clear()

    async def process_high_urgency(self, callback: types.CallbackQuery) -> None:

        if callback.data == CallbackDataKeys.confirm_high_urgency:
            id_to_change = callback.message.text.split()[1]

            database.execute("UPDATE requests_queue SET urgency=? WHERE id=?", (1, id_to_change))
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

        await callback.message.answer(client_card, reply_markup=keyboards.keyboard_student_card_actions())

        await state.update_data(idt=idt)
        await state.update_data(prev_msg_id=message_id)
        await state.set_state(ShowClientCard.further_actions)

    async def change_task(self, message: types.Message, state: FSMContext, task_number: int):
        data = await state.get_data()
        task_field = "task_first" if task_number == 1 else "task_second"
        task_id = database.last_added_id(data["idt"])

        database.execute(
            f"UPDATE tasks SET {task_field} = ? WHERE id = ? AND (status = 1 OR status = 5)",
            (message.text, task_id)
        )

        await message.answer(f"✅ Задание {task_number} изменено", reply_markup=keyboards.keyboard_main_teacher())
        await message.bot.send_message(data["idt"], f"🛠 Задание {task_number} обновлено оператором")
        await state.clear()

    async def set_all_tasks(self, message: types.Message, state: FSMContext, task_one: str, task_two: str):
        data = await state.get_data()
        now = datetime.datetime.now(timezone.utc)

        to_insert = [(int(data["idt"]), task_one, task_two, now.strftime("%Y-%m-%d %H:%M:%S"), 1, 0)]

        database.execute(
            "INSERT INTO tasks VALUES (NULL, ?, ?, ?, ?, ?, ?)", to_insert
        )

        request_id = database.fetchall("SELECT id FROM tasks WHERE idt=?", (data['idt'],))[-1]

        await message.answer(StudentMessages.SUCESSFULLY_ADDED_TASKS.format(request_id=request_id),
                             reply_markup=keyboards.keyboard_main_teacher())
        await state.clear()

    async def add_penalty(self, callback: types.CallbackQuery, state: FSMContext, reason):
        data = await state.get_data()

        client = Client(data['idt'])
        client_card = client.full_card()

        database.execute("INSERT INTO penalty VALUES (NULL, ?, ?)", (data["idt"], client.penalties_reason_map[reason]))

        # await message.delete()
        await callback.message.edit_text("✅ Штраф добавлен\n\n" + client_card, reply_markup=keyboards.keyboard_student_card_actions())
        await callback.bot.send_message(client.telegram_id, f"⚠️ Вам назначен штраф: <b>{client.penalties_reason_map[reason]}</b>.")

        await state.set_state(ShowClientCard.further_actions)

    async def add_penalty_with_photo(self, message: types.Message, state: FSMContext, reason, photo):
        data = await state.get_data()

        client = Client(data['idt'])
        client_card = client.full_card()

        database.execute("INSERT INTO penalty VALUES (NULL, ?, ?)", (data["idt"], client.penalties_reason_map[reason]))

        await message.answer("✅ Штраф добавлен\n\n" + client_card, reply_markup=keyboards.keyboard_student_card_actions())
        await message.bot.send_photo(client.telegram_id, caption=f"⚠️ Вам назначен штраф: <b>{client.penalties_reason_map[reason]}</b>.", photo=photo)

        await state.set_state(ShowClientCard.further_actions)

    async def remove_penalty(self, message: types.Message, penalty_id: int, state: FSMContext):
        data = await state.get_data()

        # Verify that the penalty exists and belongs to the current client
        existing_penalty = database.fetchall(
            "SELECT id FROM penalty WHERE id = ? AND idt = ?", (penalty_id, data["idt"])
        )

        if not existing_penalty:
            await message.answer("❌ Штраф с таким ID не найден у этого пользователя.")
            return

        # Proceed with deletion if valid
        database.execute("DELETE FROM penalty WHERE id = ?", (penalty_id,))

        client = Client(data['idt'])
        client_card = client.full_card()

        await message.bot.delete_message(message.from_user.id, data["msg_id"])
        await message.delete()
        await message.answer("✅ Штраф удалён\n\n" + client_card, reply_markup=keyboards.keyboard_student_card_actions())

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
            alias_result = database.fetchall("SELECT alias FROM detail_aliases WHERE name=?", (name,))
            alias = alias_result[0] if alias_result else name[:5].upper()
            summary_lines.append(f"🔸 <b>{alias}</b> (<i>{name}</i>): <b>{len(items)}</b> шт.")
        summary = "\n".join(summary_lines) if summary_lines else "<b>Нет деталей в инвентаре.</b>"

        if isinstance(callback, types.CallbackQuery):
            await callback.message.edit_text(summary, parse_mode=ParseMode.HTML,
                                             reply_markup=keyboards.keyboard_inventory())
        else:
            await callback.answer(summary, parse_mode=ParseMode.HTML, reply_markup=keyboards.keyboard_inventory())

    async def show_bucket(self, callback: types.CallbackQuery, state: FSMContext):
        await self.form_message_with_bucket(callback, state)

        await state.set_state(AliasLookupState.waiting_for_alias)

    async def inventory_add_start(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "<b>Введите название детали</b> и <b>цену</b> через запятую.\nПример: <i>Arduino Mega, 1500</i>",
            reply_markup=keyboards.keyboard_alias_back(),
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
            reply_markup=keyboards.keyboard_inventory(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()

    async def process_alias_lookup(self, message: types.Message, state: FSMContext):
        user_alias = message.text.strip().upper()

        result = database.fetchall("SELECT name FROM detail_aliases WHERE alias=?", (user_alias,))
        if not result:
            await message.answer(
                "❌ <b>Ошибка:</b> Объект с алиасом <i>{}</i> не найден.".format(user_alias),
                reply_markup=keyboards.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        full_name = result[0]

        details = database.fetchall_multiple("SELECT id, name, price, owner FROM details WHERE name=?", (full_name,))
        if not details:
            await message.answer(
                "❌ <b>Ошибка:</b> Нет деталей с именем <i>{}</i> в инвентаре.".format(full_name),
                reply_markup=keyboards.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        # output = await form_message_detail_info(message, state, details)

        cost = details[0][2]  # Assuming the price is stored at index 2.
        owner_name_map = Operator.get_idt_name_map()

        output_lines = [f"💰 <b>Цена:</b> {cost}", "📦 <b>Объекты:</b>"]
        for detail in details:
            obj_id = detail[0]
            owner_id = detail[3]
            if owner_id and owner_id in owner_name_map:
                owner_name = f"{owner_name_map[owner_id][0]} {owner_name_map[owner_id][1]}"
            else:
                owner_name = "Нет владельца"
            output_lines.append(f"🔹 <b>ID:</b> {obj_id} | <b>Владелец:</b> {owner_name}")

        output = "\n".join(output_lines)

        await message.answer(output, reply_markup=keyboards.keyboard_transfer_return(), parse_mode=ParseMode.HTML)
        await state.clear()

    async def transfer_item(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "Введите <b>ID объекта</b> и <b>ID нового владельца</b> через запятую.\nПример: <i>23, 987654321</i>",
            reply_markup=keyboards.keyboard_alias_back(),
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
                reply_markup=keyboards.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        if not Detail.detail_exists(obj_id):
            await message.answer(
                f"❌ <b>Ошибка:</b> Объект с ID <b>{obj_id}</b> не найден в инвентаре.",
                reply_markup=keyboards.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        if not BaseUser.user_exists(new_owner):
            await message.answer(
                f"❌ <b>Ошибка:</b> Пользователь с ID <b>{new_owner}</b> не найден в системе.",
                reply_markup=keyboards.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        database.execute("UPDATE details SET owner=? WHERE id=?", (new_owner, obj_id))
        await message.answer(
            f"✅ Объект с ID <b>{obj_id}</b> успешно передан пользователю <b>{new_owner}</b>.",
            reply_markup=keyboards.keyboard_transfer_return(),
            parse_mode=ParseMode.HTML
        )
        # await form_message_with_bucket(message, state)
        await state.set_state(AliasLookupState.waiting_for_alias)

    async def return_item(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "Введите <b>ID объекта</b> для возврата.\nПример: <i>23</i>",
            reply_markup=keyboards.keyboard_alias_back(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(ItemActionState.waiting_for_return_info)

    async def process_return_item(self, message: types.Message, state: FSMContext):
        try:
            obj_id = int(message.text.strip())
        except ValueError:
            await message.answer(
                "❌ <b>Ошибка:</b> Введите корректный числовой ID объекта.",
                reply_markup=keyboards.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        if not Detail.detail_exists(obj_id):
            await message.answer(
                f"❌ <b>Ошибка:</b> Объект с ID <b>{obj_id}</b> не найден в инвентаре.",
                reply_markup=keyboards.keyboard_alias_back(),
                parse_mode=ParseMode.HTML
            )
            return

        database.execute("UPDATE details SET owner=NULL WHERE id=?", (obj_id,))
        await message.answer(
            f"✅ Объект с ID <b>{obj_id}</b> успешно возвращён в инвентарь.",
            reply_markup=keyboards.keyboard_transfer_return(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()

    # async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    #     None
