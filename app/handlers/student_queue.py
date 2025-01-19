from aiogram.enums import ParseMode
from aiogram import F
from app.utilits import keyboards
from aiogram import types, Router
from app.handlers.teacher import status_int_to_str
from app.utilits.database import database

router = Router()


def generate_message_to_send(students_messages) -> str:
    message_to_send = [
        (f"<b>ID</b>: {students_messages[i][0]}\n"
         f"<b>Статус</b>: {status_int_to_str(students_messages[i][4])}\n---\n") for i in range(len(students_messages))]

    s = 'Очередь заданий: \n---\n'
    if len(message_to_send) == 0:
        s += "Очередь заданий пуста!"
    else:
        for a in message_to_send:
            s += a
    return s


@router.callback_query(F.data == "student_requests")
async def student_requests(callback: types.CallbackQuery):
    students_messages = database.fetchall_multiple(f"SELECT * FROM requests_queue "
                                                   f"WHERE proceeed!=2 "
                                                   f"AND idt={callback.from_user.id}")

    await callback.message.edit_text(generate_message_to_send(students_messages),
                                     reply_markup=keyboards.keyboard_back_to_main_student(), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data == "back_to_main_student")
async def student_requests(callback: types.CallbackQuery):
    await callback.message.edit_text("Выбирайте, <b>Клиент!</b>",
                                     reply_markup=keyboards.keyboard_main_student(), parse_mode=ParseMode.HTML)
    await callback.answer()
