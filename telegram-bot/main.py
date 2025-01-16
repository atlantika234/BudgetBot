'''Добавь отдельный файл routes и проработай архитектуру'''

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from app.settings import config
from states import Category, Expences as ExpanceState, Earning as EarningState
from aiogram.types import ReplyKeyboardMarkup
from enum import Enum
from filters import SumFilter

logging.basicConfig(level=logging.INFO)
default=DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=config.TELEGRAM_BOT_TOKEN, default=default)

dp = Dispatcher()

messages_to_delete = []

'''Вспомагательные функции, перенести в файл helper.py'''
async def clean_chat(chat_id: int):
    for message_id in messages_to_delete:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass
    messages_to_delete.clear()

def create_category_keyboard(categories: Enum) -> ReplyKeyboardMarkup:
    kb = [[types.KeyboardButton(text=category)] for category in categories]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)



'''Переписать start на menu, а start сделать более презентабельным'''
@dp.message(StateFilter(None), Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Додати запис про витрату")],
        [types.KeyboardButton(text="Додати запис про надходження")],
        [types.KeyboardButton(text="Список витрат")],
        [types.KeyboardButton(text="Список надходжень")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    msg = await message.answer("Це меню керування ботом\n"
                               "Натисніть кнопки нижче", reply_markup=keyboard)
    messages_to_delete.append(msg.message_id)

async def main():
    await dp.start_polling(bot)

@dp.message(F.text, Command("list_expances"))
async def cmd_test1(message: types.Message):
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    msg = await message.answer("<b>this is command for list expance</b>")
    messages_to_delete.append(msg.message_id)

@dp.message(F.text, Command("list_earnings"))
async def cmd_test2(message: types.Message):
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    msg = await message.answer("this is command for list ernings")
    messages_to_delete.append(msg.message_id)



'''Блоки про `витрати` и `надходження` переписать в 1 кусок кода который вызывается 2 раза, ибо все кроме их вызова индентично'''

# витрати
@dp.message(F.text.lower() == "додати запис про витрату")
async def add_expance(message: types.Message, state: FSMContext):
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    msg = await message.answer("Оберіть категроію", reply_markup=create_category_keyboard(Category))
    messages_to_delete.append(msg.message_id)
    await state.set_state(ExpanceState.category)

@dp.message(ExpanceState.category)
async def add_expance_sum(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    msg = await message.answer("Введіть суму")
    messages_to_delete.append(msg.message_id)
    await state.set_state(ExpanceState.sum)


@dp.message(ExpanceState.sum, SumFilter())
async def add_expance_description(message: types.Message, state: FSMContext):
    await state.update_data(sum=message.text)
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Без опису")]], resize_keyboard=True
    )
    msg = await message.answer("Введіть опис для витрати, якщо без опису натисніть кнопку нижче", reply_markup=keyboard)
    messages_to_delete.append(msg.message_id)
    await state.update_data(bot_message=msg.message_id)
    await state.set_state(ExpanceState.description)

'''Задебажить обработчик, если корректно ввести данные все хорошо, но если нет, то ничего не запускается'''
@dp.message(EarningState.sum)
async def add_expance_sum_failed(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    msg = await message.reply("Введіть коректну суму(числом)")
    messages_to_delete.append(msg.message_id)

@dp.message(ExpanceState.description)
async def final_expance(message: types.Message, state: FSMContext):
    if message.text.lower() == 'без опису':
        await state.update_data(description='')
    else:
        await state.update_data(description=message.text)
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


    answers = await state.get_data()
    description_msg = answers.get("description")
    msg = await message.answer(f"<b>Категорія:    {answers.get("category")}"
                               f"\nСума: {answers.get("sum")}грн"
                               f"{'' if description_msg == '' else f' \nОпис:         {description_msg}'}</b>")
    del description_msg
    messages_to_delete.append(msg.message_id)
    messages_to_delete.append(msg.message_id)
    await state.clear()

# надходження
@dp.message(F.text.lower() == "додати запис про надходження")
async def add_expance(message: types.Message, state: FSMContext):
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    msg = await message.answer("Оберіть категроію", reply_markup=create_category_keyboard(Category))
    messages_to_delete.append(msg.message_id)
    await state.set_state(ExpanceState.category)

@dp.message(ExpanceState.category)
async def add_expance_sum(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    msg = await message.answer("Введіть суму")
    messages_to_delete.append(msg.message_id)
    await state.set_state(ExpanceState.sum)


@dp.message(ExpanceState.sum, SumFilter())
async def add_expance_description(message: types.Message, state: FSMContext):
    await state.update_data(sum=message.text)
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Без опису")]], resize_keyboard=True
    )
    msg = await message.answer("Введіть опис для витрати, якщо без опису натисніть кнопку нижче", reply_markup=keyboard)
    messages_to_delete.append(msg.message_id)
    await state.update_data(bot_message=msg.message_id)
    await state.set_state(ExpanceState.description)
'''Задебажить обработчик, если корректно ввести данные все хорошо, но если нет, то ничего не запускается'''
@dp.message(EarningState.sum)
async def add_expance_sum_failed(message: types.Message, state: FSMContext):
    print(f"Текущее состояние: {await state.get_state()}")
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    msg = await message.reply("Введіть коректну суму(числом)")
    messages_to_delete.append(msg.message_id)

@dp.message(ExpanceState.description)
async def final_expance(message: types.Message, state: FSMContext):
    if message.text.lower() == 'без опису':
        await state.update_data(description='')
    else:
        await state.update_data(description=message.text)
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


    answers = await state.get_data()
    description_msg = answers.get("description")
    msg = await message.answer(f"<b>Категорія:    {answers.get("category")}"
                               f"\nСума: {answers.get("sum")}грн"
                               f"{'' if description_msg == '' else f' \nОпис:         {description_msg}'}</b>")
    del description_msg
    messages_to_delete.append(msg.message_id)
    msg = await message.answer("/menu")
    messages_to_delete.append(msg.message_id)
    await state.clear()



@dp.message(F.text, Command("help"))
async def cmd_test1(message: types.Message):
    await clean_chat(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    msg = await message.answer("/list_earnings  this is command for list ernings\n"
                               "/list_expances  this is command for list expances\n"
                               "/add_earnings   this is command for add ernings\n"
                               "/add_expances   this is command for add expances")
    messages_to_delete.append(msg.message_id)

if __name__ == "__main__":
    asyncio.run(main())