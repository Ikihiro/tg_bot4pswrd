from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import MessageNotModified

from keyboards.inline.pagination import item_pagination_keyboard, pagination_callback, item_callback, \
    pwd_keyboard
from keyboards.inline.start_keyboard import start_callback, to_start_keyboard
from loader import dp, db


@dp.callback_query_handler(pagination_callback.filter(page="current_page"))
@dp.callback_query_handler(pagination_callback.filter(page="current_page"), state="update_gen_pwd")
@dp.callback_query_handler(pagination_callback.filter(page="nothing_page"))
@dp.callback_query_handler(pagination_callback.filter(page="nothing_page"), state="update_gen_pwd")
@dp.callback_query_handler(pagination_callback.filter(page="first_last_page"))
@dp.callback_query_handler(pagination_callback.filter(page="first_last_page"), state="first_last_page")
async def current_page(call: types.CallbackQuery):
    await call.answer(cache_time=60)


@dp.message_handler(Command("get_password"), state="*")
@dp.callback_query_handler(start_callback.filter(key="get_pwd"))
@dp.callback_query_handler(start_callback.filter(key="get_pwd"), state="pwd")
@dp.callback_query_handler(start_callback.filter(key="get_pwd"), state="update_pwd")
async def ask_password(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await state.finish()
    text = ("Здесь находятся ваши кодовые слова🫥\n"
            "Выберите кодовое слово, пароль которого хотите увидеть😎")
    if isinstance(message, types.Message):
        user_id = message.from_user.id
        array = await db.select_pwd(telegram_id=user_id)
        if array:
            await message.answer(text, reply_markup=item_pagination_keyboard(array))
        else:
            await message.answer("У вас нет кодовых слов и паролей🫥\n"
                                 "Создайте пароль и возвращайтесь🙃", reply_markup=to_start_keyboard)
    if isinstance(message, types.CallbackQuery):
        call = message
        user_id = call.from_user.id
        array = await db.select_pwd(telegram_id=user_id)
        await call.answer()
        if array:
            await call.message.edit_text(text, reply_markup=item_pagination_keyboard(array))
        else:
            await call.message.edit_text("У вас нет кодовых слов и паролей🫥\n"
                                         "Создайте пароль и возвращайтесь🙃", reply_markup=to_start_keyboard)


@dp.callback_query_handler(pagination_callback.filter(key="items"))
@dp.callback_query_handler(pagination_callback.filter(key="items"), state="update_gen_pwd")
async def update_page(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    array = await db.select_pwd(telegram_id=user_id)
    page = int(callback_data.get("page"))
    try:
        await call.message.edit_reply_markup(reply_markup=item_pagination_keyboard(array, page=page))
        await call.answer()
    except MessageNotModified:
        await call.answer()


@dp.callback_query_handler(item_callback.filter())
@dp.callback_query_handler(item_callback.filter(), state="update_pwd")
async def get_password(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    text = (
        f"Кодовое слово: <code>{callback_data.get('site')}</code>\n"
        f"Ваш пароль: <code>{callback_data.get('pwd')}</code>"
    )
    await state.set_state("pwd")
    async with state.proxy() as data:
        data["pwd_id"] = callback_data.get("id")
        data["site"] = callback_data.get("site")
        data["pwd"] = callback_data.get("pwd")
    await call.answer()
    await call.message.edit_text(text, reply_markup=pwd_keyboard)
