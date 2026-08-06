from aiogram.fsm.state import StatesGroup, State


class PaymentState(StatesGroup):
    payment_id = State()
