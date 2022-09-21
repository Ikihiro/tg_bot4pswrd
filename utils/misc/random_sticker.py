import random

from loader import db


async def get_random_sticker(mood: str):
    stickers = await db.select_sticker(mood=mood)
    try:
        random_stick = random.choice(stickers)
    except IndexError:
        random_stick = None
    return random_stick
