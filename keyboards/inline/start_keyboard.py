from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.callback_datas import menu_cd

start_callback = CallbackData("start_keyboard", "key")

start_markup = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить пароль", callback_data=start_callback.new(key="add_pwd")),
            InlineKeyboardButton(text="Смотреть пароли", callback_data=start_callback.new(key="get_pwd")),
        ],
        [
            InlineKeyboardButton(text="Сгенерировать пароль", callback_data=start_callback.new(key="gen_pwd")),
        ]
    ]
)

to_start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data=menu_cd.new(code="to_start"))
        ]
    ]
)
