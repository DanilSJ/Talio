from aiogram.fsm.state import StatesGroup, State


class AdminSystemPromptState(StatesGroup):
    text = State()


class AdminADSState(StatesGroup):
    text = State()
