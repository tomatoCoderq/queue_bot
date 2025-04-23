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


class ShowClientCard(StatesGroup):
    set_tasks_two = State()
    set_tasks_one = State()
    get_client_id = State()
    get_changed_task = State()
    further_actions = State()
    get_penalty_reasons = State()
    get_whether_wants_photo = State()
    waiting_penalty_photo = State()
    get_penalty_id_to_delete = State()


class ReturnToQueue(StatesGroup):
    waiting_id = State()
    waiting_approve_reject = State()


class ItemActionState(StatesGroup):
    waiting_for_transfer_info = State()
    waiting_for_return_info = State()


class AliasLookupState(StatesGroup):
    waiting_for_alias = State()


class InventoryAddState(StatesGroup):
    waiting_for_detail_info = State()
