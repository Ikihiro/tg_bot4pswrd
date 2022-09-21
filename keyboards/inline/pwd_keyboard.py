from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.callback_datas import menu_cd
from keyboards.inline.start_keyboard import start_callback


gen_pwd_callback = CallbackData("pwd", "operation")


gen_pwd_keyboards = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Обновить пароль", callback_data=gen_pwd_callback.new(operation="update_pwd")),
            InlineKeyboardButton(text="Добавить пароль", callback_data=gen_pwd_callback.new(operation="attach_pwd")),
        ],
        [
            InlineKeyboardButton(text="Выйти", callback_data=menu_cd.new(code="to_start"))
        ]
    ]
)


pwd = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton("Получить сохраненный пароль🤨", callback_data="pwd")
        ]
    ]
)

get_pwd_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Смотреть пароли",
                callback_data=start_callback.new(key="get_pwd")
            )
        ]
    ]
)
