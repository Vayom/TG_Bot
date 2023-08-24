from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    Weather = State()
    START = State()
    GIVING_ITEM = State()
    LOAD_ITEM = State()
