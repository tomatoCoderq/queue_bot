import os

from aiogram.fsm.context import FSMContext

from aiogram import F, types, Router
from aiogram.types import FSInputFile

from app.utilits import keyboards

from app.utilits.keyboards import CallbackDataKeys
from app.utilits.messages import TeacherMessages

router = Router()


@router.callback_query(F.data == CallbackDataKeys.xlsx)
async def get_xlsx(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer_document(document=FSInputFile(os.getenv("FILE")),
                                           reply_markup=keyboards.keyboard_back_to_main_teacher_no_edit())


@router.callback_query(F.data == CallbackDataKeys.back_to_main_teacher_no_edit)
async def back_to_main_teacher_no_edit(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    await callback.message.answer(TeacherMessages.CHOOSE_MAIN_TEACHER,
                                  reply_markup=keyboards.keyboard_main_teacher())
    await state.clear()
