from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from keyboards.inline import cancel
from loader import dp, db
from states import Sticker


# Отправляет пользователю все стикеры из таблицы stickers
# @dp.message_handler(Command("all_stickers"))
# async def get_all_stickers(message: types.Message):
#     stickers = await db.select_all_stickers()
#     for stick in stickers:
#         await message.answer(f"{stick.get('id')} - {stick.get('mood')}")
#         await message.answer_sticker(stick.get('url'))


# Добавление стикера первый функционал
@dp.message_handler(Command("add_sticker"))
async def ask_mood(message: types.Message):
    await message.answer("Напишите настроение стикера (good, bad и т.д.)", reply_markup=cancel)
    await Sticker.S1.set()


# Для первого стейта Стикер
@dp.message_handler(state=Sticker.S1, content_types=[types.ContentType.TEXT])
async def ask_sticker(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["mood"] = message.text
    await message.answer("Пришлите теперь стикер, который хотите добавить☺️", reply_markup=cancel)
    await Sticker.next()


@dp.message_handler(state=Sticker.S1, content_types=[types.ContentType.ANY])
async def err_ask_sticker(message: types.Message):
    await message.answer("Напишите символами настроение стикера😎",
                         reply_markup=cancel)


# Для второго стейта Стикера
@dp.message_handler(state=Sticker.S2, content_types=[types.ContentType.STICKER])
async def add_sticker(message: types.Message, state: FSMContext):
    sticker_id = message.sticker.file_id
    async with state.proxy() as data:
        mood = data["mood"]
    await db.add_sticker(mood, sticker_id)
    await message.answer("Стикер добавлен в базу данных🟢", reply_markup=cancel)
    await state.finish()


@dp.message_handler(state=Sticker.S2)
async def err_sticker(message: types.Message):
    await message.answer("Пришлите стикер 🥸\n"
                         "Попробуйте прислать еще раз😃",
                         reply_markup=cancel)
