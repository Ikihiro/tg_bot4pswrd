from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.callback_datas import menu_cd
from keyboards.inline.start_keyboard import start_callback

pagination_callback = CallbackData("pagination", "key", "page")
item_callback = CallbackData("item", "id", "site", "pwd")
pwd_callback = CallbackData("pwd", "operation")


# Кнопка для операция над паролем
pwd_keyboard = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Обновить пароль", callback_data=pwd_callback.new(operation="update_pwd")),
            InlineKeyboardButton(text="Удалить пароль", callback_data=pwd_callback.new(operation="delete_pwd")),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=start_callback.new(key="get_pwd")),
        ]
    ]
)


# Функция для пагинации кодовых слов
def item_pagination_keyboard(array, page: int = 1):
    key = "items"
    MAX_KEYBOARD_BUTTONS = 5
    row_width = 2
    count_items = len(array)
    first_item_index = (page-1) * MAX_KEYBOARD_BUTTONS
    last_item_index = page * MAX_KEYBOARD_BUTTONS

    sliced_array = array[first_item_index:last_item_index]

    items_buttons = list()
    for item in sliced_array:
        items_buttons.append(
            InlineKeyboardButton(
                text=f"{item.get('site')}",
                callback_data=item_callback.new(id=item.get('id'), site=item.get('site'), pwd=item.get('pwd'))
            )
        )

    first_page = 1
    first_page_text = f"{first_page} << "
    previous_page = page - 1
    previous_page_text = f"{previous_page} < "
    current_page = page
    next_page = page + 1
    next_page_text = f" > {next_page}"
    if count_items % MAX_KEYBOARD_BUTTONS == 0:
        max_page = count_items // MAX_KEYBOARD_BUTTONS
    else:
        max_page = count_items // MAX_KEYBOARD_BUTTONS + 1
    last_page_text = f" >> {max_page}"

    pages_buttons = list()

    if previous_page >= first_page:
        pages_buttons.append(
            InlineKeyboardButton(
                text=first_page_text,
                callback_data=pagination_callback.new(key=key, page=first_page)
            )
        )
        pages_buttons.append(
            InlineKeyboardButton(
                text=previous_page_text,
                callback_data=pagination_callback.new(key=key, page=previous_page)
            )
        )
    else:
        pages_buttons.append(
            InlineKeyboardButton(
                text=first_page_text,
                callback_data=pagination_callback.new(key=key, page="first_last_page")
            )
        )
        pages_buttons.append(
            InlineKeyboardButton(
                text=' . ',
                callback_data=pagination_callback.new(key=key, page="nothing_page")
            )
        )

    pages_buttons.append(
        InlineKeyboardButton(
            text=f" -- {current_page} -- ",
            callback_data=pagination_callback.new(key=key, page="current_page")
        )
    )

    if next_page <= max_page:
        pages_buttons.append(
            InlineKeyboardButton(
                text=next_page_text,
                callback_data=pagination_callback.new(key=key, page=next_page)
            )
        )
        pages_buttons.append(
            InlineKeyboardButton(
                text=last_page_text,
                callback_data=pagination_callback.new(key=key, page=max_page)
            )
        )
    else:
        pages_buttons.append(
            InlineKeyboardButton(
                text=' . ',
                callback_data=pagination_callback.new(key=key, page="nothing_page")
            )
        )
        pages_buttons.append(
            InlineKeyboardButton(
                text=last_page_text,
                callback_data=pagination_callback.new(key=key, page="first_last_page")
            )
        )

    markup = InlineKeyboardMarkup(row_width=row_width)
    for button in items_buttons:
        markup.insert(button)

    markup.row(*pages_buttons)
    markup.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=menu_cd.new(code="to_start")
        )
    )
    return markup
