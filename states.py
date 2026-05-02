from aiogram.fsm.state import StatesGroup, State

class TestState(StatesGroup):
    choosing_test = State()
    passing_test = State()