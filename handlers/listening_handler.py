from aiogram import Router
from aiogram.types import Message
from utils.database import Database
from config import DB_NAME
from aiogram.filters import Command

from rapidfuzz import process

import requests
import json


listen_router = Router()
db = Database(DB_NAME)

@listen_router.message(Command('voice'))
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


@listen_router.message()
async def searching(message: Message):
    word = message.text
    words_en = db.get_en_all()
    words_uz = db.get_uz_all()
    words_uz = [w[0] for w in words_uz]
    words_en = [w[0] for w in words_en]

    result_en = process.extract(f"{word.strip().lower()}", words_en, limit=2)
    result_uz = process.extract(f"{word.strip().lower()}", words_uz, limit=2)

    info = ''
    if result_en:
        print(result_en)
        for w in result_en:
            if w[1] >= 99:
                info += "* "
            info += f"<blockquote><b><code>{w[0]}</code> — {db.get_uz_from_en(w[0])[0]} — {db.get_ru_from_uz(db.get_uz_from_en(w[0])[0])[0]}</b></blockquote>\n"
    if result_uz:
        info += '\n'
        for w in result_uz:
            if w[1] >= 99:
                info += "* "
            info += f"<blockquote><b><code>{w[0]}</code> — {db.get_en_from_uz(w[0])[0]} —— {db.get_ru_from_uz(w[0])[0]}</b></blockquote>\n"
    else:
        info = "Natija topilmadi("

    print(result_en)
    print(result_uz)

    await message.reply(info)









