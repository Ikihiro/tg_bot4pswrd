import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline import cancel
from keyboards.inline.pagination import pwd_callback, item_callback
from keyboards.inline.pwd_keyboard import get_pwd_keyboard
from loader import dp, db
from utils.misc.random_sticker import get_random_sticker


@dp.callback_query_handler(pwd_callback.filter(operation="update_pwd"), state="pwd")
async def ask_new_pwd(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        pwd_id = data.get("pwd_id")
        site = data.get("site")
        pwd = data.get('pwd')
    await call.message.edit_text(
        "Напишите новый пароль, чтобы обновить пароль",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data=item_callback.new(id=pwd_id, site=site, pwd=pwd))
                ]
            ]
        )
    )
    await state.set_state("update_pwd")


@dp.message_handler(state="update_pwd", regexp=re.compile(r"^[0-9a-zA-z!@#$%^&*()+.;':]{,18}$"))
async def update_pwd(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pwd_id = data.get("pwd_id")
    obj_pwd = (await db.select_pwd(id=int(pwd_id)))[0]
    telegram_id, site, pwd = obj_pwd.get("telegram_id"), obj_pwd.get("site"), message.text
    await db.update_pwd(telegram_id=telegram_id, site=site, pwd=pwd)
    await message.answer('---------- Ваш пароль изменен ----------', reply_markup=get_pwd_keyboard)


@dp.message_handler(state="update_pwd")
async def err_update_pwd(message: types.Message):
    mood = "bad"
    sticker = await get_random_sticker(mood)
    text = (f"Неправильно введен пароль: <code>{message.text}</code> ⭕️\n"
            "Пароль должен быть не длинее 18 символов\n"
            "И состоять из цифр, или латинских букв, или спец. символов\n"
            "<pre>** Попробуйте написать еще раз✅ **</pre>")
    await message.answer_sticker(sticker=sticker.get("url"))
    await message.answer(text, reply_markup=cancel)


@dp.callback_query_handler(pwd_callback.filter(operation="delete_pwd"), state="pwd")
async def delete_pwd(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        pwd_id = data.get("pwd_id")
    await db.delete_pwd(id=int(pwd_id))
    await call.message.edit_text("---------- Пароль успешно удален ----------", reply_markup=get_pwd_keyboard)
    await state.finish()
