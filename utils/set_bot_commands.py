from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("help", "Вывести справку"),
            types.BotCommand("set_password", "Создать пароль"),
            types.BotCommand("get_password", "Получить пароль"),
            types.BotCommand("gen_password", "Сгенерировать пароль"),
            types.BotCommand("add_sticker", "Добавить стикер"),
            types.BotCommand("cancel", "Выйти из машины состояния"),
        ]
    )
