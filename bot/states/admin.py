from aiogram.fsm.state import StatesGroup, State

class BroadcastStates(StatesGroup):
    waiting_for_content = State()
    preview = State()