from aiogram.types import Message
from aiogram.filters import Filter

class IsNumberFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        text = message.text.replace(',', '.').strip()
        try:
            float(text)
            return True
        except ValueError:
            return False

class SumFilter(IsNumberFilter):
    pass