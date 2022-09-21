from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp


@dp.message_handler(state="*", content_types=types.ContentType.ANY)
async def state_off(message: types.Message, state: FSMContext):
    await state.finish()
