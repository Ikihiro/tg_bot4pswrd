import re
from typing import Union

import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline import cancel
from keyboards.inline.callback_datas import menu_cd
from keyboards.inline.pagination import item_pagination_keyboard, item_callback
from keyboards.inline.pwd_keyboard import gen_pwd_keyboards, gen_pwd_callback, get_pwd_keyboard
from keyboards.inline.start_keyboard import start_callback
from loader import dp, db
from utils.misc.random_sticker import get_random_sticker


async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


@dp.message_handler(Command("gen_password"), state="*")
@dp.callback_query_handler(start_callback.filter(key="gen_pwd"))
@dp.callback_query_handler(menu_cd.filter(code="to_start"), state="update_gen_pwd")
@dp.callback_query_handler(menu_cd.filter(code="to_gen_pwd"), state=["gen_pwd", "ask_code_word"])
async def get_gen_pwd(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await state.finish()
    URL = "https://passwordinator.herokuapp.com?num=True&caps=True"
    response = await get(URL)
    pwd = response[9:-2]
    text = f"Ваш пароль: <code>{pwd}</code>"

    if isinstance(message, types.Message):
        await message.answer(text=text)
    elif isinstance(message, types.CallbackQuery):
        await state.set_state("gen_pwd")
        async with state.proxy() as data:
            data["gen_pwd"] = pwd
        call = message
        await call.answer()
        await call.message.edit_text(
            text=text,
            reply_markup=gen_pwd_keyboards,
        )


# Хендлер для обновления пароля кодового слова
@dp.callback_query_handler(gen_pwd_callback.filter(operation="update_pwd"), state=["gen_pwd"])
async def choose_site(call: types.CallbackQuery, state: FSMContext):
    array = await db.select_pwd(telegram_id=call.from_user.id)

    if array:
        await call.message.edit_text(
            "Выберите кодовое слово, пароль которого хотите изменить",
            reply_markup=item_pagination_keyboard(array)
        )
        await state.set_state("update_gen_pwd")
    else:
        await call.message.edit_text(
            "У вас нет кодовых слов и паролей🫥\n"
            "Создайте пароль и возвращайтесь🙃",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton("Назад", callback_data=menu_cd.new(code="to_gen_pwd"))]]
            )
        )


@dp.callback_query_handler(item_callback.filter(), state="update_gen_pwd")
async def update_gen_pwd(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()

    mood = "good"
    sticker = await get_random_sticker(mood)
    site, pwd = callback_data.get('site'), callback_data.get('pwd')
    async with state.proxy() as data:
        gen_pwd = data.get("gen_pwd")
    await db.update_pwd(telegram_id=call.from_user.id, site=site, pwd=gen_pwd)
    await call.message.answer_sticker(sticker.get('url'))
    await call.message.answer(
        text=f"---------- Пароль обновлен ----------\n\n"
             f"Новый пароль кодового слова [<code>{site}</code>]\n\n"
             f"---------- <code>{gen_pwd}</code> ----------",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton("Назад", callback_data=menu_cd.new(code="to_start"))]]
        )
    )
    await state.finish()


# Создание объекта сгенерированным паролем
@dp.callback_query_handler(gen_pwd_callback.filter(operation="attach_pwd"), state=["gen_pwd"])
async def ask_site(call: types.CallbackQuery, state: FSMContext):

    await call.message.edit_text(
        "Напишите кодовое слово, на который хотите\n"
        "прикрепить сгенерированный пароль",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton("Назад", callback_data=menu_cd.new("to_gen_pwd"))]]
        )
    )
    await state.set_state("ask_code_word")


@dp.message_handler(state=["ask_code_word"], regexp=re.compile(r"^[0-9a-zA-zа-яА-Я!@#$%^&*()+.;':]{1,18}$"))
async def create_gen_pwd(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        gen_pwd = data.get("gen_pwd")
    mood = "good"
    sticker = await get_random_sticker(mood)
    await db.add_pwd(telegram_id=message.from_user.id, site=message.text, pwd=gen_pwd)
    await message.answer_sticker(sticker.get('url'))
    await message.answer("---------- Пароль создан! ----------\n"
                         "Можете посмотреть пароли по кнопке ниже",
                         reply_markup=get_pwd_keyboard)
    await state.finish()


@dp.message_handler(state="ask_code_word", content_types=types.ContentType.ANY)
async def err_site(message: types.Message):
    mood = "bad"
    sticker = await get_random_sticker(mood)
    text = (f"Неправильно введено кодовое слово: <code>{message.text}</code> ⭕️\n"
            "Кодовое слово должно быть не больше 18 символов\n"
            "И состоять из цифр, или латинских букв, или спец. символов\n"
            "<pre>** Попробуйте написать еще раз✅ **</pre>")
    await message.answer_sticker(sticker.get('url'))
    await message.answer(text, reply_markup=cancel)
