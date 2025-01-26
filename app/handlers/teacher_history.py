from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F

from app.utilits import keyboards

from aiogram import Bot, types, Router
from app.handlers.teacher import generate_message_to_send
from loguru import logger

from app.utilits.database import database
from app.utilits.keyboards import CallbackDataKeys

from app.utilits.messages import TeacherMessages

router = Router()


class ReturnToQueue(StatesGroup):
    waiting_id = State()
    waiting_approve_reject = State()


@router.callback_query(F.data == CallbackDataKeys.history)
async def history(callback: types.CallbackQuery, state: FSMContext):
    students_messages = database.fetchall_multiple("select * from requests_queue where "
                                                   "proceeed=4 order by close_time desc limit 3")

    message_to_send = generate_message_to_send("Напишите ID, чтобы вернуть его из удаленных\n", students_messages)

    await callback.message.edit_text(message_to_send, reply_markup=keyboards.keyboard_back_to_main_teacher())
    await callback.answer()

    await state.set_state(ReturnToQueue.waiting_id)
    await state.update_data(msg_id=callback.message.message_id)


@router.message(ReturnToQueue.waiting_id, F.text)
async def return_to_queue(message: types.Message, state: FSMContext, bot: Bot):
    messages_ids = database.fetchall("select id from requests_queue where "
                                     "proceeed=4 order by close_time desc limit 3")
    data = await state.get_data()

    if not message.text.isdigit() or int(message.text) not in messages_ids:
        await message.reply(TeacherMessages.NO_ID_FOUND)
        logger.error(f"Wrong id was written by {message.from_user.username}")
        return return_to_queue

    database.execute("update requests_queue set proceeed=0 where id=?", (int(message.text),))

    await message.delete()
    await bot.delete_message(message.from_user.id, data['msg_id'])

    await message.answer("Сделано " + TeacherMessages.CHOOSE_MAIN_TEACHER,
                         reply_markup=keyboards.keyboard_main_teacher())

    await state.clear()

    # students_messages = database.fetchall_multiple("select * from requests_queue order by close_time desc limit 3;")
    # message_to_send = generate_message_to_send("Напишите ID, чтобы вернуть его из удаленных\n", students_messages)
    # await callback.message.edit_text(message_to_send, reply_markup=keyboards.keyboard_back_to_main_teacher())
    # await state.set_state(ReturnToQueue.waiting_id)
