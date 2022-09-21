from aiogram.dispatcher.filters.state import StatesGroup, State


class Pwd(StatesGroup):
    P1 = State()
    P2 = State()


class Sticker(StatesGroup):
    S1 = State()
    S2 = State()
