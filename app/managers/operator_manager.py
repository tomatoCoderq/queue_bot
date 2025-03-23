from datetime import *
from typing import Union

import aiogram.exceptions
from aiogram.types import FSInputFile

from app.handlers.teacher_tasks_queue import map_names_and_idt
from app.models.client import Client
from app.utils.messages import TeacherMessages
from app.utils.excel_writer import Excel
from app.models.operator import Operator
from app.utils.files import *

from app.fsm_states.operator_states import CheckMessage, ShowClientPenaltyCard, ReturnToQueue, ShowClientCard


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
        """
        Retrieve and display current student requests to teacher.
        Updates state with the message ID for later deletion.
        """
        students_messages = database.fetchall_multiple(
            "SELECT * FROM requests_queue WHERE proceeed=0 OR proceeed=1"
        )
        s = self.generate_message_to_send(TeacherMessages.SELECT_REQUEST, students_messages)
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
            else:
                await callback.message.delete()
                msg = await callback.message.answer(
                    s, reply_markup=keyboards.keyboard_details_teacher(), parse_mode=ParseMode.HTML
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
            await message.delete()
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
        await state.update_data(msg=msg_obj.message_id)
        logger.info(f"Set waiting_action with msg id {msg_obj.message_id}")

    async def accept_task(self, callback: types.CallbackQuery, bot: Bot, state: FSMContext):
        """Accept a task by updating its status and notifying the client."""
        data = await state.get_data()
        messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0")
        if data['id'] in messages_ids:
            database.execute("UPDATE requests_queue SET proceeed=1 WHERE id=?", (data['id'],))
            logger.success("Task accepted")
            await self.operator.send_message(bot, TeacherMessages.REQUEST_ACCEPTED.format(id=data['id']))
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
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            bot,
            TeacherMessages.PHOTO_SENT_TO_STUDENT,
            reply_markup=keyboards.keyboard_main_teacher(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()
        logger.success("Finished work report, state cleared.")

    @staticmethod
    async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
        """Return to the main teacher menu."""
        # await Operator.edit_message(bot=callback.bot,
        #                                  text=TeacherMessages.CHOOSE_MAIN_TEACHER,
        #                                  message_id=callback.message.message_id,
        #                                  reply_markup=keyboards.keyboard_main_teacher())

        await callback.message.edit_text(
            TeacherMessages.CHOOSE_MAIN_TEACHER,
            reply_markup=keyboards.keyboard_main_teacher()
        )
        await callback.answer()
        await state.clear()

    async def back_to_main_teacher_no_edit(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete()

        await callback.message.answer(TeacherMessages.CHOOSE_MAIN_TEACHER,
                                      reply_markup=keyboards.keyboard_main_teacher())
        await state.clear()

    async def back_to_details(self, callback: types.CallbackQuery, state: FSMContext):
        """Return to the teacher details view."""
        if callback.message.document:
            await callback.message.answer(
                TeacherMessages.CHOOSE_MAIN_TEACHER,
                reply_markup=keyboards.keyboard_details_teacher()
            )
            await callback.message.delete()
        else:
            await self.operator.edit_message(bot=callback.bot,
                                             text=TeacherMessages.CHOOSE_MAIN_TEACHER,
                                             message_id=callback.message.message_id,
                                             reply_markup=keyboards.keyboard_details_teacher())
            # await callback.message.edit_text(
            #     TeacherMessages.CHOOSE_MAIN_TEACHER,
            #     reply_markup=keyboards.keyboard_details_teacher()
            # )
        await callback.answer()
        await state.clear()

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

        client = Client(idt, "qw")

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

    async def add_penalty(self, message: types.Message, state: FSMContext, reason: str):
        data = await state.get_data()
        database.execute("INSERT INTO penalty VALUES (NULL, ?, ?)", (data["idt"], reason))
        await message.answer("✅ Штраф добавлен", reply_markup=keyboards.keyboard_main_teacher())

    async def remove_penalty(self, message: types.Message, penalty_id: int):
        database.execute("DELETE FROM penalty WHERE id = ?", (penalty_id,))
        await message.answer("✅ Штраф удалён", reply_markup=keyboards.keyboard_main_teacher())

    async def back_to_main_teacher(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            TeacherMessages.CHOOSE_MAIN_TEACHER,
            reply_markup=keyboards.keyboard_main_teacher(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        await state.clear()


class OperatorManagerEquipment(OperatorManager):
    def __init__(self, operator: Operator):
        super().__init__(operator)

    async def show_bucket(callback: types.CallbackQuery, state: FSMContext):
        None

    async def inventory_add_start(callback: types.CallbackQuery, state: FSMContext):
        None

    async def process_inventory_add(message: types.Message, state: FSMContext):
        None

    async def process_alias_lookup(message: types.Message, state: FSMContext):
        None

    async def transfer_item(callback: types.CallbackQuery, state: FSMContext):
        None

    async def process_transfer_item(message: types.Message, state: FSMContext):
        None

    async def return_item(callback: types.CallbackQuery, state: FSMContext):
        None

    async def process_return_item(message: types.Message, state: FSMContext):
        None

    async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
        None
