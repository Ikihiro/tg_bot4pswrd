from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import menu_cd


cancel = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Выйти", callback_data=menu_cd.new(code="to_start"))
        ]
    ]
)
