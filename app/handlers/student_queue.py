from aiogram.enums import ParseMode
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.utilits import keyboards
from aiogram import types, Router, Bot
from app.handlers.teacher import status_int_to_str
from app.utilits.database import database
from app.utilits.messages import TeacherMessages, StudentMessages
from loguru import logger


router = Router()

class DeleteOwnQueue(StatesGroup):
    get_id_to_delete = State()


def generate_message_to_send(students_messages) -> str:
    message_to_send = [
        (f"<b>ID</b>: {students_messages[i][0]}\n"
         f"<b>Файл</b>: {students_messages[i][8]}.{students_messages[i][3]}\n"
         f"<b>Статус</b>: {status_int_to_str(students_messages[i][4])}\n---\n") for i in range(len(students_messages))]

    s = ('Если вы хотите удалить один из своих запросов, введите его ID! '
         'Удаляйте только неудачные или неправильно отправленные детали.\n'
         'Очередь заданий: \n---\n')
    if len(message_to_send) == 0:
        s += "Очередь заданий пуста!"
    else:
        for a in message_to_send:
            s += a
    return s


@router.callback_query(F.data == "student_requests")
async def student_requests(callback: types.CallbackQuery, state: FSMContext):
    students_messages = database.fetchall_multiple(f"SELECT * FROM requests_queue "
                                                   f"WHERE proceeed!=2 and proceeed!=4 "
                                                   f"AND idt={callback.from_user.id}")

    await callback.message.edit_text(generate_message_to_send(students_messages),
                                     reply_markup=keyboards.keyboard_back_to_main_student(), parse_mode=ParseMode.HTML)
    await callback.answer()
    await state.set_state(DeleteOwnQueue.get_id_to_delete)
    await state.update_data(msg_id=callback.message.message_id)


@router.message(DeleteOwnQueue.get_id_to_delete, F.text)
async def get_id_to_delete(message: types.Message, state: FSMContext, bot: Bot):
    messages_ids = database.fetchall("SELECT id FROM requests_queue WHERE proceeed=0 or proceeed=1")
    data = await state.get_data()

    if not message.text.isdigit() or int(message.text) not in messages_ids:
        await message.reply(TeacherMessages.NO_ID_FOUND, parse_mode=ParseMode.HTML)
        logger.error(f"Wrong id was written by {message.from_user.username}")
        return get_id_to_delete

    await bot.delete_message(message.chat.id, data['msg_id'])
    # await message.delete()
    database.execute(f"UPDATE requests_queue SET proceeed=2 WHERE id=?", (message.text, ))
    await message.answer(StudentMessages.SUCESSFULLY_DELETED, reply_markup=keyboards.keyboard_main_student())
    await state.clear()


@router.callback_query(F.data == "back_to_main_student")
async def student_requests(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выбирайте, <b>Клиент!</b>",
                                     reply_markup=keyboards.keyboard_main_student(), parse_mode=ParseMode.HTML)
    await callback.answer()
    await state.clear()
