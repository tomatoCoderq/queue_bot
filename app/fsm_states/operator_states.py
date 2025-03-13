from aiogram.fsm.state import StatesGroup, State


class CheckMessage(StatesGroup):
    waiting_id = State()
    waiting_action = State()
    waiting_size = State()
    waiting_photo_report = State()


class ShowClientPenaltyCard(StatesGroup):
    get_client_id = State()
    further_actions = State()
    get_penalty_reasons = State()
    get_penalty_id_to_delete = State()


class ReturnToQueue(StatesGroup):
    waiting_id = State()
    waiting_approve_reject = State()