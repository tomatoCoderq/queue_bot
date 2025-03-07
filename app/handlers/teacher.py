from datetime import datetime

import aiogram.exceptions
from aiogram.enums import ParseMode

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from aiogram.filters import Command

from app.utilits import keyboards

from aiogram import Bot, types, Router
from loguru import logger
import os
import shutil

from app.utilits.database import database
from app.utilits.keyboards import CallbackDataKeys
from app.utilits.messages import TeacherMessages, StudentMessages
from app.utilits.excel_writer import Excel

teacher_router = Router()


class MessageState(StatesGroup):
    waiting_message = State()
    waiting_approve_reject = State()


class CheckMessage(StatesGroup):
    waiting_id = State()
    waiting_action = State()
    waiting_size = State()
    waiting_photo_report = State()


# Form names connected only with student table
# Delete all previous attention messages
def create_idt_name_map() -> dict[str, tuple[str, str]]:
    database.execute("""
    SELECT requests_queue.idt, students.name, students.surname FROM requests_queue INNER JOIN students
    ON requests_queue.idt = students.idt
    """)

    idt_name_map = {row[0]: (row[1], row[2]) for row in database.cursor.fetchall()}

    return idt_name_map


def urgency_int_to_str(urgency: int) -> str:
    if urgency == 1:
        return "Высокая"
    if urgency == 2:
        return "Средняя"
    if urgency == 3:
        return "Низкая"


def status_int_to_str(status: int) -> str:
    if status == 0:
        return "Не в работе"
    if status == 1:
        return "В работе"


def generate_message_to_send(message, students_messages) -> str:
    try:
        cidt_name_map = create_idt_name_map()
    except KeyError as e:
        logger.error(f"Occurred {e}")
        return "<b>Ошибка!</b>"

    response = [
        (f"<b>ID</b>: {students_messages[i][0]} | "
         f"{cidt_name_map[students_messages[i][1]][0]} "
         f"{cidt_name_map[students_messages[i][1]][1]} | "
         f"{students_messages[i][8]}.<i>{students_messages[i][3]}</i>\n"
         f"<b>Количество</b>: {students_messages[i][7]} | "
         f"<b>Срочность</b>: {urgency_int_to_str(students_messages[i][2])} | "
         f"<b>Статус</b>: {status_int_to_str(students_messages[i][4])}\n---\n") for i in range(len(students_messages))]

    message_to_send = message
    if len(response) == 0:
        message_to_send += TeacherMessages.NO_REQUESTS
    else:
        for a in response:
            message_to_send += a
    return message_to_send


@teacher_router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await message.answer(TeacherMessages.CANCEL_PROCESS, reply_markup=keyboards.keyboard_main_teacher(),
                         parse_mode=ParseMode.HTML)

    await state.clear()


@teacher_router.callback_query(F.data == CallbackDataKeys.details_queue_teacher)
async def details_queue_teacher(callback: types.CallbackQuery, bot: Bot, state: FSMContext) -> object:
    await callback.message.edit_text("Действия:", reply_markup=keyboards.keyboard_details_teacher())


@teacher_router.callback_query(F.data.in_({"sort_urgency", "sort_date", "sort_type"}))
async def sort(callback: types.CallbackQuery, state: FSMContext) -> None:
    # students_messages = []
    # if callback.data == "sort_urgency":
    #     students_messages = database.fetchall_multiple("SELECT * FROM requests_queue "
    #                                                    "WHERE proceeed=0 OR proceeed=1 order by urgency")
    # if callback.data == "sort_date":
    #     students_messages = database.fetchall_multiple("SELECT * FROM requests_queue "
    #                                                    "WHERE proceeed=0 OR proceeed=1 ORDER BY time")
    # if callback.data == "sort_type":
    #     students_messages = database.fetchall_multiple("SELECT * FROM requests_queue "
    #                                                    "WHERE proceeed=0 OR proceeed=1 ORDER BY type")
    #
    # s = generate_message_to_send(students_messages)
    #
    # try:
    #     await callback.message.edit_text(s, reply_markup=keyboards.keyboard_sort_teacher(), parse_mode=ParseMode.HTML)
    # except TelegramBadRequest as e:
    #     # TODO: Change this handling
    #     None
    #
    # await state.set_state(CheckMessage.waiting_id)
    # logger.info(f"{callback.message.from_user.username} sets state CheckMessage.waiting_id")

    await callback.answer("Сортировки временно не работают")


@teacher_router.callback_query(F.data.in_({"back_to_queue", "check"}))
async def check_messages(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    students_messages = database.fetchall_multiple("SELECT * FROM requests_queue WHERE proceeed=0 OR proceeed=1")

    s = generate_message_to_send(TeacherMessages.SELECT_REQUEST, students_messages)

    try:
        # ToDO: Rewrite this division
        if callback.data == "check":
            if len(s) > 4096:
                for x in range(0, len(s), 4096):
                    msg = await callback.message.answer(s[x:x + 4096],
                                                        parse_mode=ParseMode.HTML)
                msg = await callback.message.answer("Выбирайте:", reply_markup=keyboards.keyboard_sort_teacher())
            else:
                msg = await callback.message.edit_text(s, reply_markup=keyboards.keyboard_sort_teacher(),
                                                       parse_mode=ParseMode.HTML)
        else:
            # await bot.delete_message(callback.message.from_user.id, data['msg'])
            await callback.message.delete()
            msg = await callback.message.answer(s, reply_markup=keyboards.keyboard_details_teacher(),
                                                parse_mode=ParseMode.HTML)
    except aiogram.exceptions.TelegramBadRequest as e:
        logger.error(f"Occurred {e}")

    await state.set_state(CheckMessage.waiting_id)
    logger.info(f"{callback.message.from_user.username} sets state CheckMessage.waiting_id")

    await state.update_data(msg=msg.message_id)

    logger.info(f"{callback.message.from_user.username} updates state data msg={msg.message_id}")

    await callback.answer()


@teacher_router.message(CheckMessage.waiting_id, F.text)
async def waiting_id(message: types.Message, state: FSMContext, bot: Bot) -> object:
    # Fix taking all data and putting info whether it was taken or not
    messages_students = database.fetchall_multiple("SELECT * FROM requests_queue WHERE proceeed=0 OR proceeed=1")
    messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0 or proceeed=1")
    students_ids = database.fetchall("SELECT idt FROM requests_queue WHERE proceeed=0 or proceeed=1")

    if not message.text.isdigit() or int(message.text) not in messages_ids:
        await message.reply(TeacherMessages.NO_ID_FOUND, parse_mode=ParseMode.HTML)
        logger.error(f"Wrong id was written by {message.from_user.username}")
        return check_messages

    spdict = {messages_ids[i]: students_ids[i] for i in range(len(messages_ids))}

    data = await state.get_data()

    # Delete previous message and message sent by user
    try:
        await bot.delete_message(message.from_user.id, data['msg'])
        await message.delete()
    except (aiogram.exceptions.TelegramBadRequest, KeyError) as e:
        await message.answer(TeacherMessages.ID_ERROR)
        logger.error(f"Occurred {e}")
    logger.info(f"Deleting message from user and previous message with id {data['msg']}")

    message_to_send = ''

    cidt_name_map = create_idt_name_map()

    for i in range(len(messages_students)):
        if messages_students[i][0] == int(message.text):
            message_to_send = (f"<b>ID</b>: {messages_students[i][0]}\n"
                               f"<b>Имя</b>: {cidt_name_map[messages_students[i][1]][0]} "
                               f"{cidt_name_map[messages_students[i][1]][1]}\n"
                               f"<b>Срочность</b>: {urgency_int_to_str(messages_students[i][2])}\n"
                               f"<b>Тип</b>: {messages_students[i][3]}\n"
                               f"<b>Дата отправки</b>: {messages_students[i][5]}\n"
                               f"<b>Комментарий</b>: {messages_students[i][6]}\n"
                               f"<b>Количество</b>: {messages_students[i][7]}\n")
            await state.update_data(id=messages_students[i][0],
                                    idt=messages_students[i][1],
                                    type=messages_students[i][3])
            break

    # Find file name with specific ID given by user
    file_name = [entry for entry in os.listdir(f'students_files/{spdict[int(message.text)]}') if
                 entry.startswith(message.text)]

    is_proceed = database.fetchall("SELECT proceeed FROM requests_queue WHERE id=?", (message.text,))[0]

    if is_proceed == 0:
        msg = await message.answer_document(
            document=types.FSInputFile(f"students_files/{spdict[int(message.text)]}/{file_name[0]}"),
            caption=message_to_send, reply_markup=keyboards.keyboard_teacher_actions_one(), parse_mode=ParseMode.HTML)
    if is_proceed == 1:
        msg = await message.answer_document(
            document=types.FSInputFile(f"students_files/{spdict[int(message.text)]}/{file_name[0]}"),
            caption=message_to_send, reply_markup=keyboards.keyboard_teacher_actions_two(), parse_mode=ParseMode.HTML)

    await state.set_state(CheckMessage.waiting_action)
    logger.info(f"{message.from_user.username} sets state CheckMessage.waiting_action")

    await state.update_data(msg=msg.message_id)
    logger.info(f"{message.from_user.username} updates state data msg={msg.message_id}")


@teacher_router.callback_query(CheckMessage.waiting_action, F.data == CallbackDataKeys.accept_detail)
async def take_on_work(callback: types.CallbackQuery, bot: Bot, state: FSMContext) -> object:
    data = await state.get_data()
    messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0")

    if data['id'] in messages_ids:
        database.execute(f"UPDATE requests_queue SET proceeed=1 WHERE id=?", (data['id'],))

        logger.success("File was taken in work")
        await bot.send_message(data['idt'], TeacherMessages.REQUEST_ACCEPTED.format(id=data['id']))
        await callback.answer("Принято в работу", reply_markup=keyboards.keyboard_main_teacher())
    else:
        logger.error("File was already taken in work")
        await callback.answer(TeacherMessages.REQUEST_ALREADY_IN_WORK, reply_markup=keyboards.keyboard_main_teacher())
        return waiting_id


@teacher_router.callback_query(CheckMessage.waiting_action, F.data == CallbackDataKeys.reject_detail)
async def reject_task(callback: types.CallbackQuery, bot: Bot, state: FSMContext) -> object:
    data = await state.get_data()
    messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0")

    if data['id'] in messages_ids:
        # delete_file(data)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        database.execute(f"UPDATE requests_queue SET proceeed=4 WHERE id=?", (data['id'],))
        database.execute("UPDATE requests_queue SET close_time=? WHERE id=?", (current_time, data['id']))

        logger.success("File was rejected")
        await bot.send_message(data['idt'], TeacherMessages.REQUEST_REJECTED.format(id=data['id']))
        await callback.answer("Отклонено", reply_markup=keyboards.keyboard_main_teacher())
        await callback.message.delete()
        await callback.message.answer(TeacherMessages.CHOOSE_MAIN_TEACHER,
                                      reply_markup=keyboards.keyboard_main_teacher())
    else:
        logger.error("File was already taken in work")
        await callback.answer(TeacherMessages.REQUEST_ALREADY_IN_WORK, reply_markup=keyboards.keyboard_main_teacher())
        return waiting_id


@teacher_router.callback_query(CheckMessage.waiting_action, F.data == CallbackDataKeys.end_task)
async def finish_work(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    is_proceed = database.fetchall(f"SELECT proceeed FROM requests_queue WHERE id=?", (data['id'],))[0]

    if is_proceed == 0:
        await callback.answer(TeacherMessages.REQUEST_NOT_IN_WORK)
        return waiting_id
    if is_proceed == 1:
        await callback.message.delete()
        if data['type'] == "stl":
            msg = await callback.message.answer(TeacherMessages.SEND_WEIGHT_REPORT,
                                                parse_mode=ParseMode.HTML)
        if data['type'] == "dxf":
            msg = await callback.message.answer(TeacherMessages.SEND_SIZE_REPORT,
                                                parse_mode=ParseMode.HTML)
        await state.set_state(CheckMessage.waiting_size)
        await callback.answer()
        await state.update_data(msg=msg.message_id)
        logger.info(f"{callback.message.from_user.username} sets state CheckMessage.waiting_size")


@teacher_router.message(CheckMessage.waiting_size, F.text)
async def finish_work_get_params(message: types.Message, state: FSMContext):
    data = await state.get_data()

    if data['type'] == "stl" and not message.text.isdigit():
        await message.answer(StudentMessages.INVALID_AMOUNT_INPUT)
        return finish_work_get_params

    if data['type'] == "dxf" and len(message.text.split()) != 2:
        await message.answer(TeacherMessages.INVALID_SIZE_INPUT)
        return finish_work_get_params

    if len(message.text.split()) == 2:
        if data['type'] == "dxf" and not message.text.split()[0].isdigit() or not message.text.split()[1].isdigit():
            await message.answer(StudentMessages.INVALID_AMOUNT_INPUT)
            return finish_work_get_params

    to_set = 0
    if data['type'] == "stl":
        to_set = message.text
    if data['type'] == "dxf":
        # Calculating area
        to_set = int(message.text.split()[0]) * int(message.text.split()[1])

    database.execute("UPDATE requests_queue SET params=? WHERE id=?", (to_set, data['id']))

    await message.answer(TeacherMessages.SEND_PHOTO_REPORT)
    await state.set_state(CheckMessage.waiting_photo_report)


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


def move_file(data) -> None:
    messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0 or proceeed=1")
    students_ids = database.fetchall("SELECT idt FROM requests_queue WHERE proceeed=0 or proceeed=1")

    spdict = {messages_ids[i]: students_ids[i] for i in range(len(messages_ids))}

    try:
        document_name = [entry for entry in os.listdir(f'students_files/{spdict[int(data["id"])]}') if
                         entry.startswith(str(data['id']))]
        if not os.path.exists(f"permanent/{spdict[data['id']]}"):
            os.makedirs(f"permanent/{spdict[data['id']]}")

        # os.remove(f"students_files/{spdict[data['id']]}/{document_name[0]}")
        shutil.move(f"students_files/{spdict[data['id']]}/{document_name[0]}",
                    f"permanent/{spdict[data['id']]}/{document_name[0]}")
        logger.success(f"Moved file to permanent/{spdict[data['id']]}/{document_name[0]}")
    except (OSError, KeyError, shutil.Error) as e:
        logger.error(f"Occurred {e}")


# os.replace(f"temporal/{data['idt']}{current_time}.jpg", f"permanent/{data['idt']}{current_time}/.jpg")

@teacher_router.message(CheckMessage.waiting_photo_report, F.photo)
async def finish_work_report(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    excel_table = Excel()

    await bot.delete_message(message.from_user.id, int(data['msg']))

    excel_table.write(database.fetchall_multiple("select * from requests_queue where id=?", (data['id'],)))

    move_file(data)

    database.execute(f"UPDATE requests_queue SET proceeed=2 WHERE id=?", (data['id'],))

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_name = f"temporal/{data['idt']}{current_time}.jpg"
    open(file_name, "w").close()

    await bot.download(message.photo[-1], f"temporal/{data['idt']}{current_time}.jpg")
    await bot.send_photo(data['idt'], photo=types.FSInputFile(f"temporal/{data['idt']}{current_time}.jpg"),
                         caption=f"Ваша работа с ID {data['id']} завершена!")

    try:
        os.remove(f"temporal/{data['idt']}{current_time}.jpg")
    except OSError as e:
        logger.error(f"Occurred {e}")

    await message.answer(TeacherMessages.PHOTO_SENT_TO_STUDENT,
                         parse_mode=ParseMode.HTML, reply_markup=keyboards.keyboard_main_teacher())

    await state.clear()
    logger.success("CheckMessage FSM was cleared")


@teacher_router.callback_query(F.data == "back_to_main_teacher")
async def back_to_main_teacher(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.edit_text(TeacherMessages.CHOOSE_MAIN_TEACHER,
                                     reply_markup=keyboards.keyboard_main_teacher())

    await callback.answer()
    await state.clear()


@teacher_router.callback_query(F.data == "back_to_details_teacher")
async def back_to_main_teacher(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    if callback.message.document:
        await callback.message.answer(TeacherMessages.CHOOSE_MAIN_TEACHER,
                                      reply_markup=keyboards.keyboard_details_teacher())
        await callback.message.delete()

    else:
        await callback.message.edit_text(TeacherMessages.CHOOSE_MAIN_TEACHER,
                                         reply_markup=keyboards.keyboard_details_teacher())

    await callback.answer()
    await state.clear()
