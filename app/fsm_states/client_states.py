from aiogram.fsm.state import StatesGroup, State


class SendPiece(StatesGroup):
    waiting_urgency = State()
    waiting_amount = State()
    waiting_comments = State()
    waiting_file = State()
