from aiogram import Router
from aiogram.types import Message

import requests
import json


listen_router = Router()

@listen_router.message()
async def en_to_voice(message: Message):
    word = message.text
    response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    if response.status_code == 200:
        data = json.loads(response.text)
        voice = data[0]['phonetics'][1]['audio']
        await message.delete()
        await message.answer_voice(voice=voice, caption=message.text)
    else:
        await message.reply("❌Xatolik yuz berdi, faqat Ingliz tilidagi so'zlarni kiriting")


