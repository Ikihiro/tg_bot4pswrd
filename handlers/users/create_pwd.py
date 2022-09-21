import re
from typing import Union

import asyncpg
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from keyboards.inline import cancel
from keyboards.inline.pwd_keyboard import get_pwd_keyboard
from keyboards.inline.start_keyboard import to_start_keyboard, start_callback
from loader import dp, db
from states import Pwd
from utils.misc.random_sticker import get_random_sticker


@dp.message_handler(Command('set_password'), state="*")
@dp.callback_query_handler(start_callback.filter(key="add_pwd"))
async def ask_site(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await state.finish()
    text = "Напиши пожалуйста кодовое слово📎\nНа который будет прикреплен твой пароль📂"
    if isinstance(message, types.Message):
        await message.answer(text)
        await Pwd.first()
    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.answer()
        await call.message.edit_text(text, reply_markup=to_start_keyboard)
        await Pwd.first()


# Для первого стейта Pwd
@dp.message_handler(state=Pwd.P1, regexp=re.compile(r"^[0-9a-zA-z!@#$%^&*()+.;':]{,18}$"))
async def ask_pwd(message: types.Message, state: FSMContext):
    await message.answer("Напиши теперь пароль🔑")
    async with state.proxy() as data:
        data["site"] = message.text
    await Pwd.next()


@dp.message_handler(state=Pwd.P1)
async def err_site(message: types.Message):
    mood = "bad"
    sticker = await get_random_sticker(mood)
    text = (f"Неправильно введено кодовое слово: <code>{message.text}</code> ⭕️\n"
            "Кодовое слово должно быть не больше 18 символов\n"
            "И состоять из цифр, или латинских букв, или спец. символов\n"
            "<pre>** Попробуйте написать еще раз✅ **</pre>")
    await message.answer_sticker(sticker=sticker.get("url"))
    await message.answer(text, reply_markup=cancel)


# Для второго стейта Pwd
@dp.message_handler(state=Pwd.P2, regexp=re.compile(r"^[0-9a-zA-z!@#$%^&*()+.;':]{6,18}$"))
async def set_pwd(message: types.Message, state: FSMContext):
    await message.delete()
    async with state.proxy() as data:
        site = data["site"]
    try:
        await db.add_pwd(message.from_user.id, site, message.text)
        mood = "good"
        sticker = await get_random_sticker(mood)
        if sticker:
            await message.answer_sticker(sticker.get("url"))
        else:
            await message.answer(f"Стикер с настроением <code>{mood}</code>😁😆🥹")
        await message.answer(
            "--------- Пароль сохранен, доступен по кнопке ниже⬇️ ---------",
            reply_markup=get_pwd_keyboard
        )
        await state.finish()
    except asyncpg.exceptions.UniqueViolationError:
        mood = "bad"
        sticker = await get_random_sticker(mood)
        if sticker:
            await message.answer_sticker(sticker.get("url"))
        else:
            await message.answer(f"Стикер с настроением <code>{mood}</code>😁😆🥹")
        await message.answer("Такой пароль уже сохранен в нашей базе данных❌\n"
                             "** Попробуйте напишите еще раз!✅ **",
                             reply_markup=cancel)


@dp.message_handler(state=Pwd.P2)
async def err_pwd(message: types.Message):
    mood = "bad"
    sticker = await get_random_sticker(mood)
    text = (f"Неправильно введен пароль: <code>{message.text}</code> ⭕️\n"
            "Пароль должен быть длинее 5 символов\n"
            "И не больше 18 символов\n"
            "И состоять из цифр, или латинских букв, или спец. символов\n"
            "<pre>** Попробуйте написать еще раз✅ **</pre>")
    await message.answer_sticker(sticker=sticker.get("url"))
    await message.answer(text, reply_markup=cancel)
