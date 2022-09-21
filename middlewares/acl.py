import asyncpg
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from loader import db


class ACLMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        try:
            user = await db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
        except asyncpg.exceptions.UniqueViolationError:
            user = await db.select_user(telegram_id=message.from_user.id)
        data["user"] = user
