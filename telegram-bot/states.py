from aiogram.fsm.state import State, StatesGroup
from enum import Enum

class Category(Enum):
    FOOD = "Їжа"
    TRANSPORT = "Транспорт"
    ENTERTAINMENT = "Разваги"
    OTHER = "Інше"

Category = Category

class Expences(StatesGroup):
    title = State()
    sum = State()
    description = State()
    date = State()
    category = State()

class Earning(StatesGroup):
    title = State()
    sum = State()
    description = State()
    date = State()
    category = State()