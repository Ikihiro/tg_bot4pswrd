from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Command
from aiogram.utils.exceptions import MessageCantBeEdited

from keyboards.inline.callback_datas import menu_cd
from keyboards.inline.start_keyboard import start_markup
from loader import dp
from states import Pwd, Sticker


@dp.callback_query_handler(
    menu_cd.filter(code="to_start"),
    state=[Pwd.P1, Pwd.P2, Sticker.S1, Sticker.S2, "gen_pwd", "ask_code_word"]
)
@dp.callback_query_handler(menu_cd.filter(code="to_start"))
@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    text = (f"Привет, {message.from_user.full_name}!👋\n"
            f"Этот бот будет сохранять твои пароли🗝\n"
            f"И выдавать тебе их при запросе📩\n"
            f"Также умеет генерировать пароли.")
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=start_markup)
    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text, reply_markup=start_markup)
    await state.finish()


@dp.message_handler(Command("cancel"), state="*")
async def cancel_all(message: types.Message, state: FSMContext):
    await state.finish()
    try:
        await message.edit_reply_markup()
    except MessageCantBeEdited:
        pass
