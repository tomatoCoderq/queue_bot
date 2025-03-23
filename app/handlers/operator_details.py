from app.utils.files import *
from app.models.operator import Operator
from app.managers.operator_manager import OperatorManagerDetails
from app.fsm_states.operator_states import CheckMessage, ReturnToQueue
from app.utils.filters import IsTeacher

teacher_router = Router()


# Base class: Represents each user

# TeacherManager Class: Encapsulates teacher-specific business logic

# -----------------------------
# Aiogram Handlers Using the OOP Classes
# -----------------------------

@teacher_router.message(Command("cancel"), IsTeacher())
async def cancel_handler(message: types.Message, state: FSMContext):
    teacher = Operator(message.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.cancel_process(message, state)


@teacher_router.callback_query(F.data == CallbackDataKeys.details_queue_teacher)
async def details_queue_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.show_details_queue(callback)


@teacher_router.callback_query(F.data.in_({"back_to_queue", "check", "sort_type", "sort_date", "sort_urgency"}))
async def check_messages_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.check_messages(callback, state, bot)


@teacher_router.message(CheckMessage.waiting_id, F.text)
async def waiting_id_handler(message: types.Message, state: FSMContext, bot: Bot):
    teacher = Operator(message.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.handle_waiting_id(message, state, bot)


@teacher_router.callback_query(CheckMessage.waiting_action, F.data == CallbackDataKeys.accept_detail)
async def accept_task_handler(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.accept_task(callback, bot, state)


@teacher_router.callback_query(CheckMessage.waiting_action, F.data == CallbackDataKeys.reject_detail)
async def reject_task_handler(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.reject_task(callback, bot, state)


@teacher_router.callback_query(CheckMessage.waiting_action, F.data == CallbackDataKeys.end_task)
async def finish_work_handler(callback: types.CallbackQuery, state: FSMContext):
    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.finish_work(callback, state)


@teacher_router.message(CheckMessage.waiting_size, F.text)
async def finish_work_get_params_handler(message: types.Message, state: FSMContext):
    teacher = Operator(message.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.finish_work_get_params(message, state)


@teacher_router.message(CheckMessage.waiting_photo_report, F.photo)
async def finish_work_report_handler(message: types.Message, bot: Bot, state: FSMContext):
    teacher = Operator(message.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.finish_work_report(message, bot, state)


# @teacher_router.callback_query(F.data == "back_to_main_teacher")
# async def back_to_main_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
#     teacher = Operator(callback.from_user.id)
#     manager = OperatorManagerDetails(teacher)
#     await manager.back_to_main(callback, state)


# @teacher_router.callback_query(F.data == CallbackDataKeys.back_to_main_teacher_no_edit)
# async def back_to_main_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
#     teacher = Operator(callback.from_user.id)
#     manager = OperatorManagerDetails(teacher)
#     await manager.back_to_main_teacher_no_edit(callback, state)


# @teacher_router.callback_query(F.data == "back_to_details_teacher")
# async def back_to_details_handler(callback: types.CallbackQuery, state: FSMContext):
#     teacher = Operator(callback.from_user.id)
#     manager = OperatorManagerDetails(teacher)
#     await manager.back_to_details(callback, state)


@teacher_router.callback_query(F.data == CallbackDataKeys.xlsx)
async def get_xlsx_handler(callback: types.CallbackQuery):
    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.get_xlsx(callback)


@teacher_router.callback_query(F.data == CallbackDataKeys.history)
async def history_handler(callback: types.CallbackQuery, state: FSMContext):
    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.history(callback, state)


@teacher_router.message(ReturnToQueue.waiting_id, F.text)
async def return_detail_to_queue(message: types.Message, state: FSMContext, bot: Bot):
    teacher = Operator(message.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.return_detail_to_queue(message, state, bot)


@teacher_router.callback_query(
    F.data.in_({CallbackDataKeys.confirm_high_urgency, CallbackDataKeys.reject_high_urgency}))
async def process_high_urgency_handler(callback: types.CallbackQuery) -> None:
    teacher = Operator(callback.from_user.id)
    manager = OperatorManagerDetails(teacher)
    await manager.process_high_urgency(callback)
