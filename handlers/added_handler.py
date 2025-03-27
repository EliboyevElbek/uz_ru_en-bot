import asyncio
import requests
import json

from  aiogram import Router, F
from aiogram.types import Message

from config import big_admin
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboard.inline_keyboard import sura_kb
from state.admin_state import Surah
from utils.database import Database
from config import DB_NAME

db = Database(DB_NAME)
added_router = Router()

voqia = None

@added_router.message(F.text == 'audio', F.chat.id == big_admin)
async def sura_audio_handler(message: Message):
    response = requests.get(url=f"https://quranapi.pages.dev/api/audio/56.json")
    data = json.loads(response.text)["1"]
    await message.delete()
    await message.answer_audio(audio=data["originalUrl"], caption=f"Muallif: {data['reciter']}")


@added_router.message(F.text == 'voqia', F.chat.id == big_admin)
async def sura_handler(message: Message, state: FSMContext):
    global voqia
    with open('handlers/directory/surah.txt', 'r') as file:
        voqia = file.readlines()
    voqia = [i.strip() for i in voqia]
    await state.update_data(count=0)
    await message.delete()
    await state.set_state(Surah.nextSurah)
    info = "Voqi'a surasi\n\n"
    for i, v in enumerate(voqia[:10]):
        info += f"<b><i>({i + 1}-oyat).</i> \t {v}\n\n</b>"
    inlmsg = await message.answer(
        text=info,
        reply_markup=sura_kb()
    )
    await state.update_data(inmsg=inlmsg.message_id)

@added_router.callback_query(Surah.nextSurah)
async def next_surah_handler(call: CallbackQuery, state: FSMContext):
    global voqia
    num = await state.get_data()
    count = num['count']
    info = 'Voqi\'a surasi\n\n'
    if call.data == 'next':
        count += 1
        for i, v in enumerate(voqia[10 * count : 10 * count + 10]):
            info += f"<b><i>({i + 1 + 10 * count}-oyat).</i> \t {v}\n\n</b>"
        await call.message.edit_text(
            text=info,
            reply_markup=sura_kb(count=count)
        )

    elif call.data == 'prev':
        count -= 1
        for i, v in enumerate(voqia[10 * count : 10 * count + 10]):
            info += f"<b><i>({i + 1 + 10 * count}-oyat).</i> \t {v}\n\n</b>"
        await call.message.edit_text(
            text=info,
            reply_markup=sura_kb(count=count)
        )
    elif call.data == 'edit':
        await call.answer()
        callmsg = await call.message.answer("<b>Oyat raqami bilan oyatni o'zini kiriting</b>\n\nNamuna: 7<b>*</b><i>matni...</i>")
        await state.set_state(Surah.editSurah)
        await state.update_data(callid=callmsg.message_id)
    else:
        await call.message.delete()
        await state.clear()

    await state.update_data(count=count)

@added_router.message(Surah.editSurah)
async def edit_surah(message: Message, state: FSMContext):
    global voqia
    data = await state.get_data()
    msg = message.message_id
    text = message.text.split('*')
    voqia[int(text[0]) - 1] = text[1]
    with open('handlers/directory/surah.txt', 'w') as file:
        for i in voqia:
            file.write(i.strip() + '\n')
    await message.answer('✅Muvaffaqiyatli tahrirlandi.')
    await asyncio.sleep(3)
    await message.bot.delete_messages(chat_id=message.chat.id, message_ids=[data['callid'], data['inmsg'], msg])
    await state.clear()

@added_router.message(F.text == 'from_admin_get_users', F.chat.id == big_admin)
async def get_all_users_handler(message: Message):
    users = db.get_users()
    info = ''
    if users:
        for user in users:
            info += (f"<b>Tg ID:</b> {user[0]}\n<b>Username:</b> {'@' + user[1] if user[1] else '<i>Mavjud emas</i>'}\n<b>Fullname:</b> <a href='tg://user?id={user[0]}'>{user[2]}</a>\n<b>Added: <i>{user[3]}</i></b>\n"
                     f"------------------------------------------------------\n")
        await message.reply(text=info)
    else:
        await message.reply(text="<b>Bazada foydalanuvchilar mavjud emas😐</b>")




