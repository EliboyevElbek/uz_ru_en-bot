import asyncio
import os
from random import choice, sample, shuffle

import pandas as pd
from aiogram.enums import ChatAction, PollType
from deep_translator import GoogleTranslator

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, PollAnswer
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from keyboard.inline_keyboard import get_categories_kb, between_kb, between_kb_ru
from keyboard.keyboard import off, select_word_kb, between_keyboard, quiz_stop
from state.admin_state import WordsState, NewWordState, NewWordExcel, UzWords, RuWords, Translate, EnWords, UzEnWords, \
    Quiz, QuizUzRu, QuizEnUz, QuizUzEn
from config import DB_NAME, big_admin
from utils.database import Database

word_router = Router()
db = Database(DB_NAME)

flag = False
sleep_task = None
quiz_answer = {}
succ, faild, num = 0, 0, 0

@word_router.message(Command('words'))
async def words_handler(message: Message, state: FSMContext):
    await message.answer(
        text="Qaysi toifadagi so'zlar kerak sizga, tanlang👇",
        reply_markup=get_categories_kb()
    )
    await state.set_state(WordsState.viewWords)
    await state.update_data(txt='.')


@word_router.callback_query(WordsState.viewWords)
async def view_words_handler(callback: CallbackQuery, state: FSMContext):
    all = await state.get_data()
    words = db.get_words_category(category_id=callback.data)
    words10 = [words[i: i + 10] for i in range(0, len(words), 10)]
    cat_name = db.get_category_name(id=callback.data)
    await state.update_data(words10=words10)
    await state.update_data(cat_name=cat_name)
    await state.update_data(l=0)
    await state.update_data(nishon=False)
    if words:
        await callback.message.delete()
        info = f'<b>{cat_name.upper()}</b> toifasiga tegishli so\'zlar <b>(1-{len(words[:10])})</b>\n\n\n'
        count = 1
        for word in words[:10]:
            info += (f"<blockquote><b>{count}. {word[1].lower()} ——— {word[0].lower()}</b></blockquote>"
                     f"\n\n")
            count += 1
        await callback.message.answer(
            text=f"{info}",
            reply_markup=between_kb(len(words10))
        )
        await state.set_state(WordsState.kbWords)
    else:
        txt = all['txt']
        await callback.answer("📥Bu toifa bo'sh boshqa toifani tanlang🔄", show_alert=True)
        await callback.message.edit_text(
            text=f"Qaysi toifadagi so'zlar kerak sizga, tanlang👇{txt}",
            reply_markup=get_categories_kb()
        )
        await state.update_data(txt =txt +  '.')

@word_router.callback_query(WordsState.kbWords)
async def kb_handler(call: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    cat_name = all_data['cat_name']
    words10 = all_data['words10']
    l = all_data['l']
    if call.data == 'next':
        ss = 1
        if all_data['nishon']:
            ss += 1
        l += 1
        info = f'<b>{cat_name.upper()}</b> toifasiga tegishli so\'zlar <b>({l*10 + 1}-{l*10 + len(words10[l])})</b>\n\n\n'
        count = 1
        for word in words10[l]:
            info += f"<blockquote><b>{count}. {word[ss].lower()} ——— {word[0].lower()}</b></blockquote>\n\n"
            count += 1
        if ss == 2:
            kb = between_kb_ru(len(words10), l)
        else:
            kb = between_kb(len(words10), l)
        await call.message.edit_text(
            text=info,
            reply_markup=kb
        )
    elif call.data == 'prev':
        ss = 1
        if all_data['nishon']:
            ss += 1
        l -= 1
        info = f'<b>{cat_name.upper()}</b> toifasiga tegishli so\'zlar<b>({l*10 + 1}-{l*10 + len(words10[l])})</b>\n\n\n'
        count = 1
        for word in words10[l]:
            info += f"<blockquote><b>{count}. {word[ss].lower()} ——— {word[0].lower()}</b></blockquote>\n\n"
            count += 1
        if ss == 2:
            kb = between_kb_ru(len(words10), l)
        else:
            kb = between_kb(len(words10), l)
        await call.message.edit_text(
            text=info,
            reply_markup=kb
        )
    elif call.data == 'en':
        await state.update_data(nishon=True)
        info = f'<b>{cat_name.upper()}</b> toifasiga tegishli so\'zlar<b>({l * 10 + 1}-{l * 10 + len(words10[l])})</b>\n\n\n'
        count = 1
        for word in words10[l]:
            info += f"<blockquote><b>{count}. {word[2].lower()} ——— {word[0].lower()}</b></blockquote>\n\n"
            count += 1
        await call.message.edit_text(
            text=info,
            reply_markup=between_kb_ru(len(words10), l)
        )
    elif call.data == 'uz':
        await state.update_data(nishon=False)
        info = f'<b>{cat_name.upper()}</b> toifasiga tegishli so\'zlar<b>({l * 10 + 1}-{l * 10 + len(words10[l])})</b>\n\n\n'
        count = 1
        for word in words10[l]:
            info += f"<blockquote><b>{count}. {word[1].lower()} ——— {word[0].lower()}</b></blockquote>\n\n"
            count += 1
        await call.message.edit_text(
            text=info,
            reply_markup=between_kb(len(words10), l)
        )
    elif call.data == 'save':
        tg_id = call.from_user.id
        try:
            n = db.get_loc(tg_id=tg_id)[0]
        except:
            n = None
        if n is not None:
            db.update_loc(loc=l, tg_id=tg_id)
        else:
            db.save_loc(loc=l, tg_id=tg_id)
        await call.answer("📌Eslab qolindi", show_alert=False)

    elif call.data == 'goto':
        ss = 1
        tg_id = call.from_user.id
        if all_data['nishon']:
            ss += 1
        try:
            l = db.get_loc(tg_id=tg_id)[0]
            info = f'<b>{cat_name.upper()}</b> toifasiga tegishli so\'zlar<b>({l * 10 + 1}-{l * 10 + len(words10[l])})</b>\n\n\n'
            count = 1
            for word in words10[l]:
                info += f"<blockquote><b>{count}. {word[ss].lower()} ——— {word[0].lower()}</b></blockquote>\n\n"
                count += 1
            if ss == 2:
                kb = between_kb_ru(len(words10), l)
            else:
                kb = between_kb(len(words10), l)
            await call.message.edit_text(
                text=info,
                reply_markup=kb
            )
        except:
            await call.answer("Siz sahifa saqlamagansiz", show_alert=False)

    await state.update_data(l=l)



@word_router.message(Command('new_word_add'), F.chat.id == big_admin)
async def new_add_cat_handler(message: Message, state: FSMContext):
    await state.set_state(NewWordState.selectCategory)
    await message.answer(
        text="Qaysi toifaga qo'shmoqchisiz so'zni tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(NewWordState.selectCategory)
async def new_add_handler(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data(cat_id=call.data)
    await call.message.answer(
        text="Yaxshi, endi so'zlarni quydagi formatda jo'nating\n\n"
             "(🇺🇿)  -  (🇷🇺)\n\n"
             "<b>(🇺🇿)O'zbekcha so'z-(🇺🇸)Inglizcha so'z</b>\n\n"
             "shu ko'rinishda jo'nating\n"
             "<i>Kiritib bo'lgach <b>Tugatish</b> tugmasini bosing</i>",
        reply_markup=off
    )
    await state.set_state(NewWordState.insertWords)

@word_router.message(NewWordState.insertWords)
async def insert_word_handler(message: Message, state: FSMContext):
    if message.text == 'Tugatish':
        await message.answer(
            text='🆗Muvaffaqiyatli tugatildi',
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
    else:
        cat_id = await state.get_data()
        try:
            words = message.text.split('-')
            ru_translate = GoogleTranslator(source='uz', target='ru').translate(message.text)
            if '-' in ru_translate:
                ru_translate = ru_translate.split('-')[0].lower()
            if db.word_add(uz=words[0], en=words[1], ru=ru_translate, id=cat_id['cat_id']):
                await message.reply(
                    text="✅Muvaffaqiyatli qo'shildi"
                )
            else:
                await message.reply(
                    text='⚠Noma\'lum xatolik'
                )
        except:
            await message.reply("❌Qandaydir noto'g'ri formatda jo'natdingiz, qayta to'g'irlab jo'nating🔄")


@word_router.message(Command('new_words_excel'), F.chat.id == big_admin)
async def new_words_excel_handler(message: Message, state: FSMContext):
    await state.set_state(NewWordExcel.selectCategory)
    await message.answer(
        text="Qaysi toifaga qo'shilsin, tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(NewWordExcel.selectCategory)
async def new_words_document_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    await state.update_data(cat_id=call.data)
    await call.message.answer(text="Excel documentni jo'nating\n"
                              "Format: 1-ustun <b>Uzb</b> - 2-ustun <b>English</b>")
    await state.set_state(NewWordExcel.inputExcel)

@word_router.message(NewWordExcel.inputExcel)
async def new_words_add_mb_handler(message: Message, state: FSMContext):

    async def show_typing():
        try:
            while True:
                await message.bot.send_chat_action(
                    chat_id=message.chat.id,
                    action=ChatAction.TYPING
                )
                await asyncio.sleep(3)
        except asyncio.CancelledError:
            pass

    if message.document:
        file_path = f"{message.document.file_name}"
        await message.bot.download(message.document, file_path)
        data = await state.update_data()
        df = pd.read_excel(file_path, header=None)
        os.remove(file_path)
        count = 0
        typing_task = asyncio.create_task(show_typing())
        for index, row in df.iterrows():
            if row.shape[0] == 2:
                row[2] = GoogleTranslator(source='en', target='ru').translate(row[1])
            if db.word_add(row[0], row[1], row[2], data['cat_id']):
                count += 1
            await asyncio.sleep(0)
        typing_task.cancel()

        await message.reply(f"🔢Jami {df.shape[0]} ta so'z\n✅Qo'shildi: {count} ta\n"
                            f"❌Xatolik: {df.shape[0] - count} ta")

    else:
        await message.reply(text="📥Excel document jo'nating")
    await state.clear()

@word_router.message(Command('uz_ru_select'))
async def uz_ru_select_handler(message: Message, state: FSMContext):
    await state.set_state(UzWords.selectCategory)
    await message.answer(
        text="Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(UzWords.selectCategory)
async def uz_word_handler(call: CallbackQuery, state: FSMContext):
    name = db.get_category_name(id=call.data)
    uz_words = db.get_uz_words(id=call.data)
    if uz_words:
        await call.message.delete()
        await state.set_state(UzWords.betweenSelect)
        await call.message.answer(
            text=f"<b>{name.upper()}</b> toifasidan qaysi oraliqdagi testlarni yechmoqchisiz?\n\n"
                 f"<i>Pastdagi tugmalar orqali tanlashingiz mumkin⬇️</i>",
            reply_markup=between_keyboard(id=call.data)
        )
    else:
        await call.answer("📥Bu toifa bo'sh boshqa toifani tanlang🔄", show_alert=True)
    await state.update_data(txt='.')
    await state.update_data(id=call.data)

@word_router.message(UzWords.betweenSelect)
async def uz_between_word_handler(message: Message, state: FSMContext):
    all = await state.get_data()
    between = message.text.split('-')
    name = db.get_category_name(id=all['id'])
    uz_words = db.get_uz_words(id=all['id'])[int(between[0]) - 1:int(between[1])]
    if uz_words:
        await message.answer(
            text=f"Yaxshi, {message.text} oraliqda <b>{name}</b> toifasidan men <b>O'zbekcha</b> beraman siz <b>Ruschasini</b> topasiz\n🇺🇿 🔁 ➡️ 🇷🇺",
            reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(3)
        msg = await message.answer(text="🤖Tayyormisiz? 3️⃣")
        await asyncio.sleep(1)
        for text in ["⚡️Boshlanmoqda 2️⃣...", "🚀Kettik 1️⃣"]:
            await msg.edit_text(
                text=text
            )
            await asyncio.sleep(1)
        await msg.delete()
        size = len(uz_words)
        ru_words = db.get_ru_all()
        uz = choice(uz_words)
        ru_word = db.get_ru_from_uz(uz=uz[0])
        ru_words.remove(ru_word)
        uz_words.remove(uz)
        await message.answer(
            text=f"<b>{uz[0]}</b>",
            reply_markup=select_word_kb(sample(ru_words, k=3) + [ru_word])
        )
        await state.update_data(uz_words=uz_words)
        await state.update_data(ru_words=db.get_ru_all())
        await state.update_data(ru_word=ru_word)
        await state.update_data(size=size)
        await state.update_data(count=0)
        await state.update_data(fail=0)
        await state.set_state(UzWords.nextLevel)
    else:
        txt = all['txt']
        await message.edit_text(
            text=f"Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇{txt}",
            reply_markup=get_categories_kb()
        )
        await state.update_data(txt=txt + '.')

@word_router.message(UzWords.nextLevel)
async def uz_select_handler(message: Message, state: FSMContext):
    words = await state.get_data()
    size = words['size']
    count = words['count']
    fail = words['fail']
    ru_words = words['ru_words']
    ruw = words['ru_word']
    uz_words = words['uz_words']
    if message.text == "Tugatish✖":
        await message.answer(
            text=f"<b>📊 Natijangiz:</b>\n\n"
                 f"<b>🔢 Jami so'zlar {size} ta</b>\n"
                 f"<b>✅ To'g'ri Javoblar: {count} ta</b>\n"
                 f"<b>❌ Noto'g'ri javoblar: {fail} ta</b>\n"
                 f"<b>✖️ Javob berilmaganlari: {size - count - fail} ta</b>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return
    elif message.text == ruw[0]:
        count += 1
        await state.update_data(count=count)
    else:
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(f"💡: ☑️{ruw[0]}")
        fail += 1
        await state.update_data(fail=fail)
    if uz_words:
        uz = choice(uz_words)
        ru_word = db.get_ru_from_uz(uz=uz[0])
        ru_words.remove(ru_word)
        await message.answer(
            text=f"<b>{uz[0]}</b>",
            reply_markup=select_word_kb(sample(ru_words, k=3) + [ru_word])
        )
        uz_words.remove(uz)
        await state.update_data(uz_words=uz_words)
        await state.update_data(ru_words=db.get_ru_all())
        await state.update_data(ru_word=ru_word)
    else:
        await message.answer("Ushbu toifadagi so'zlarni tugatdingiz🎉")
        await message.answer(
            text=f"<b>📊 Natijangiz:</b>\n\n"
                 f"<b>🔢 Jami so'zlar {size} ta</b>\n"
                 f"<b>✅ To'g'ri Javoblar: {count} ta</b>\n"
                 f"<b>❌ Noto'g'ri javoblar: {fail} ta</b>\n"
                 f"<b>✖️ Javob berilmaganlari: {size - count - fail} ta</b>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()


@word_router.message(Command('ru_uz_select'))
async def ru_uz_select_handler(message: Message, state: FSMContext):
    await state.set_state(RuWords.selectCategory)
    await state.update_data(txt='.')
    await message.answer(
        text="Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(RuWords.selectCategory)
async def ru_between_word_handler(call: CallbackQuery, state: FSMContext):
    name = db.get_category_name(id=call.data)
    ru_words = db.get_uz_words(id=call.data)
    if ru_words:
        await call.message.delete()
        await state.set_state(RuWords.betweenSelect)
        await call.message.answer(
            text=f"<b>{name.upper()}</b> toifasidan qaysi oraliqdagi testlarni yechmoqchisiz?\n\n"
                 f"<i>Pastdagi tugmalar orqali tanlashingiz mumkin⬇️</i>",
            reply_markup=between_keyboard(id=call.data)
        )
    else:
        await call.answer("📥Bu toifa bo'sh boshqa toifani tanlang🔄", show_alert=True)
    await state.update_data(txt='.')
    await state.update_data(id=call.data)

@word_router.message(RuWords.betweenSelect)
async def ru_word_handler(message: Message, state: FSMContext):
    all = await state.get_data()
    between = message.text.split('-')
    name = db.get_category_name(id=all['id'])
    ru_words = db.get_ru_words(id=all['id'])[int(between[0]) - 1:int(between[1])]
    if ru_words:
        await message.answer(
            text=f"Yaxshi, {message.text} oraliqda <b>{name}</b> toifasidan men <b>Ruschasini</b> beraman siz <b>O'zbekchasini</b> topasiz\n🇷🇺 🔁 ➡️ 🇺🇿",
            reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(3)
        msg = await message.answer(text="🤖Tayyormisiz? 3️⃣")
        await asyncio.sleep(1)
        for text in ["⚡️Boshlanmoqda 2️⃣...", "🚀Kettik 1️⃣"]:
            await msg.edit_text(
                text=text
            )
            await asyncio.sleep(1)
        await msg.delete()
        size = len(ru_words)
        uz_words = db.get_uz_all()

        ru = choice(ru_words)
        uz_word = db.get_uz_from_ru(ru=ru[0])
        uz_words.remove(uz_word)
        ru_words.remove(ru)

        await state.update_data(
            ru_words=ru_words,
            uz_words=uz_words,
            uz_word=uz_word,
            size=size,
            count=0,
            fail=0
        )

        await message.answer(
            text=f"<b>{ru[0]}</b>",
            reply_markup=select_word_kb(sample(uz_words, k=3) + [uz_word])
        )
        await state.update_data(ru_words=ru_words)
        await state.update_data(uz_words=db.get_uz_all())
        await state.update_data(uz_word=uz_word)
        await state.update_data(size=size)
        await state.update_data(count=0)
        await state.update_data(fail=0)
        await state.set_state(RuWords.nextLevel)
    else:
        txt = all['txt']
        await message.edit_text(
            text=f"Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇{txt}",
            reply_markup=get_categories_kb()
        )
        await state.update_data(txt=txt + '.')


@word_router.message(RuWords.nextLevel)
async def uz_select_handler(message: Message, state: FSMContext):
    words = await state.get_data()
    size = words['size']
    count = words['count']
    fail = words['fail']
    uz_words = words['uz_words']
    uzw = words['uz_word']
    ru_words = words['ru_words']
    if message.text == "Tugatish✖":
        await message.answer(
            text=f"<b>📊 Natijangiz:</b>\n\n"
                 f"<b>🔢 Jami so'zlar {size} ta</b>\n"
                 f"<b>✅ To'g'ri Javoblar: {count} ta</b>\n"
                 f"<b>❌ Noto'g'ri javoblar: {fail} ta</b>\n"
                 f"<b>✖️ Javob berilmaganlari: {size - count - fail} ta</b>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return
    elif message.text == uzw[0]:
        count += 1
        await state.update_data(count=count)
    else:
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(f"💡: ☑️{uzw[0]}")
        fail += 1
        await state.update_data(fail=fail)
    if ru_words:
        ru = choice(ru_words)
        uz_word = db.get_uz_from_ru(ru=ru[0])
        uz_words.remove(uz_word)


        await message.answer(
            text=f"<b>{ru[0]}</b>",
            reply_markup=select_word_kb(sample(uz_words, k=3) + [uz_word])
        )
        ru_words.remove(ru)
        await state.update_data(ru_words=ru_words)
        await state.update_data(uz_words=db.get_uz_all())
        await state.update_data(uz_word=uz_word)
    else:
        await message.answer("Ushbu toifadagi so'zlarni tugatdingiz🎉")
        await message.answer(
            text=f"<b>📊 Natijangiz:</b>\n\n"
                 f"<b>🔢 Jami so'zlar {size} ta</b>\n"
                 f"<b>✅ To'g'ri Javoblar: {count} ta</b>\n"
                 f"<b>❌ Noto'g'ri javoblar: {fail} ta</b>\n"
                 f"<b>✖️ Javob berilmaganlari: {size - count - fail} ta</b>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
#
# @word_router.message(Command('uz_ru_translate'))
# async def uz_ru_translate_handler(message: Message, state: FSMContext):
#     await message.reply(
#         text="Tarjima qilish uchun so'z kiriting:\n🇺🇿 🔁 ➡️ 🇷🇺",
#     )
#     await state.set_state(Translate.inputBodyUz)
#
# @word_router.message(Command('ru_uz_translate'))
# async def ru_uz_translate_handler(message: Message, state: FSMContext):
#     await message.reply(
#         text="Tarjima qilish uchun so'z kiriting:\n🇷🇺 🔁 ➡️ 🇺🇿",
#     )
#     await state.set_state(Translate.inputBodyRu)
#
# @word_router.message(Translate.inputBodyUz)
# async def uz_ru_translate_input_handler(message: Message, state: FSMContext):
#     if message.text.startswith('/'):
#         await state.clear()
#     else:
#         ru_translate = GoogleTranslator(source='uz', target='ru').translate(message.text)
#         await message.bot.send_chat_action(
#             chat_id=message.chat.id,
#             action=ChatAction.TYPING,
#         )
#         await message.reply(
#             text=ru_translate
#         )
#
# @word_router.message(Translate.inputBodyRu)
# async def ru_uz_translate_input_handler(message: Message, state: FSMContext):
#     if message.text.startswith('/'):
#         await state.clear()
#     else:
#         uz_translate = GoogleTranslator(source='ru', target='uz').translate(message.text)
#         await message.bot.send_chat_action(
#             chat_id=message.chat.id,
#             action=ChatAction.TYPING,
#         )
#         await message.reply(
#             text=uz_translate
#         )

@word_router.message(Command('en_uz_select'))
async def en_uz_select_handler(message: Message, state: FSMContext):
    await state.set_state(EnWords.selectCategory)
    await message.answer(
        text="Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(EnWords.selectCategory)
async def uz_word_handler(call: CallbackQuery, state: FSMContext):
    name = db.get_category_name(id=call.data)
    en_words = db.get_en_words(id=call.data)
    if en_words:
        await call.message.delete()
        await state.set_state(EnWords.betweenSelect)
        await call.message.answer(
            text=f"<b>{name.upper()}</b> toifasidan qaysi oraliqdagi testlarni yechmoqchisiz?\n\n"
                 f"<i>Pastdagi tugmalar orqali tanlashingiz mumkin⬇️</i>",
            reply_markup=between_keyboard(id=call.data)
        )
    else:
        await call.answer("📥Bu toifa bo'sh boshqa toifani tanlang🔄", show_alert=True)
    await state.update_data(txt='.')
    await state.update_data(id=call.data)

@word_router.message(EnWords.betweenSelect)
async def en_between_word_handler(message: Message, state: FSMContext):
    all = await state.get_data()
    between = message.text.split('-')
    name = db.get_category_name(id=all['id'])
    en_words = db.get_en_words(id=all['id'])[int(between[0]) - 1:int(between[1])]
    if en_words:
        await message.answer(
            text=f"Yaxshi, {message.text} oraliqda <b>{name}</b> toifasidan men <b>English'ni</b> beraman siz <b>O'zbekchasini</b> topasiz\n🇺🇸 🔁 ➡️ 🇺🇿",
            reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(3)
        msg = await message.answer(text="🤖Tayyormisiz? 3️⃣")
        await asyncio.sleep(1)
        for text in ["⚡️Boshlanmoqda 2️⃣...", "🚀Kettik 1️⃣"]:
            await msg.edit_text(
                text=text
            )
            await asyncio.sleep(1)
        await msg.delete()
        size = len(en_words)
        uz_words = db.get_uz_all()
        en = choice(en_words)
        uz_word = db.get_uz_from_en(en=en[0])
        en_words.remove(en)
        uz_words.remove(uz_word)
        await message.answer(
            text=f"<b>{en[0]}</b>",
            reply_markup=select_word_kb(sample(uz_words, k=3) + [uz_word])
        )
        await state.update_data(en_words=en_words)
        await state.update_data(uz_words=db.get_uz_all())
        await state.update_data(uz_word=uz_word)
        await state.update_data(size=size)
        await state.update_data(count=0)
        await state.update_data(fail=0)
        await state.set_state(EnWords.nextLevel)
    else:
        txt = all['txt']
        await message.edit_text(
            text=f"Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇{txt}",
            reply_markup=get_categories_kb()
        )
        await state.update_data(txt=txt + '.')

@word_router.message(EnWords.nextLevel)
async def uz_select_handler(message: Message, state: FSMContext):
    words = await state.get_data()
    size = words['size']
    count = words['count']
    fail = words['fail']
    en_words = words['en_words']
    uzw = words['uz_word']
    uz_words = words['uz_words']
    if message.text == "Tugatish✖":
        await message.answer(
            text=f"<b>📊 Natijangiz:</b>\n\n"
                 f"<b>🔢 Jami so'zlar {size} ta</b>\n"
                 f"<b>✅ To'g'ri Javoblar: {count} ta</b>\n"
                 f"<b>❌ Noto'g'ri javoblar: {fail} ta</b>\n"
                 f"<b>✖️ Javob berilmaganlari: {size - count - fail} ta</b>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return
    elif message.text == uzw[0]:
        count += 1
        await state.update_data(count=count)
    else:
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(f"💡: ☑️{uzw[0]}")
        fail += 1
        await state.update_data(fail=fail)
    if en_words:
        en = choice(en_words)
        uz_word = db.get_uz_from_en(en=en[0])
        uz_words.remove(uz_word)
        await message.answer(
            text=f"<b>{en[0]}</b>",
            reply_markup=select_word_kb(sample(uz_words, k=3) + [uz_word])
        )
        en_words.remove(en)
        await state.update_data(en_words=en_words)
        await state.update_data(uz_words=db.get_uz_all())
        await state.update_data(uz_word=uz_word)
    else:
        await message.answer("Ushbu toifadagi so'zlarni tugatdingiz🎉")
        await message.answer(
            text=f"<b>📊 Natijangiz:</b>\n\n"
                 f"<b>🔢 Jami so'zlar {size} ta</b>\n"
                 f"<b>✅ To'g'ri Javoblar: {count} ta</b>\n"
                 f"<b>❌ Noto'g'ri javoblar: {fail} ta</b>\n"
                 f"<b>✖️ Javob berilmaganlari: {size - count - fail} ta</b>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()

@word_router.message(Command('uz_en_select'))
async def uz_en_select_handler(message: Message, state: FSMContext):
    await state.set_state(UzEnWords.selectCategory)
    await message.answer(
        text="Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(UzEnWords.selectCategory)
async def uz_word_handler(call: CallbackQuery, state: FSMContext):
    name = db.get_category_name(id=call.data)
    uz_words = db.get_uz_words(id=call.data)
    if uz_words:
        await call.message.delete()
        await state.set_state(UzEnWords.betweenSelect)
        await call.message.answer(
            text=f"<b>{name.upper()}</b> toifasidan qaysi oraliqdagi testlarni yechmoqchisiz?\n\n"
                 f"<i>Pastdagi tugmalar orqali tanlashingiz mumkin⬇️</i>",
            reply_markup=between_keyboard(id=call.data)
        )
    else:
        await call.answer("📥Bu toifa bo'sh boshqa toifani tanlang🔄", show_alert=True)
    await state.update_data(txt='.')
    await state.update_data(id=call.data)

@word_router.message(UzEnWords.betweenSelect)
async def en_between_word_handler(message: Message, state: FSMContext):
    all = await state.get_data()
    between = message.text.split('-')
    name = db.get_category_name(id=all['id'])
    uz_words = db.get_uz_words(id=all['id'])[int(between[0]) - 1:int(between[1])]
    if uz_words:
        await message.answer(
            text=f"Yaxshi, {message.text} oraliqda <b>{name}</b> toifasidan men <b>O'zbekchasini</b> beraman siz <b>English'ni</b> topasiz\n🇺🇿 🔁 ➡️ 🇺🇸",
            reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(3)
        msg = await message.answer(text="🤖Tayyormisiz? 3️⃣")
        await asyncio.sleep(1)
        for text in ["⚡️Boshlanmoqda 2️⃣...", "🚀Kettik 1️⃣"]:
            await msg.edit_text(
                text=text
            )
            await asyncio.sleep(1)
        await msg.delete()
        size = len(uz_words)
        en_words = db.get_en_all()
        uz = choice(uz_words)
        en_word = db.get_en_from_uz(uz=uz[0])
        en_words.remove(en_word)
        uz_words.remove(uz)
        await message.answer(
            text=f"<b>{uz[0]}</b>",
            reply_markup=select_word_kb(sample(en_words, k=3) + [en_word])
        )
        await state.update_data(uz_words=uz_words)
        await state.update_data(en_words=db.get_en_all())
        await state.update_data(en_word=en_word)
        await state.update_data(size=size)
        await state.update_data(count=0)
        await state.update_data(fail=0)
        await state.set_state(UzEnWords.nextLevel)
    else:
        txt = all['txt']
        await message.edit_text(
            text=f"Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇{txt}",
            reply_markup=get_categories_kb()
        )
        await state.update_data(txt=txt + '.')

@word_router.message(UzEnWords.nextLevel)
async def uz_select_handler(message: Message, state: FSMContext):
    words = await state.get_data()
    size = words['size']
    count = words['count']
    fail = words['fail']
    en_words = words['en_words']
    enw = words['en_word']
    uz_words = words['uz_words']
    if message.text == "Tugatish✖":
        await message.answer(
            text=f"<b>📊 Natijangiz:</b>\n\n"
                 f"<b>🔢 Jami so'zlar {size} ta</b>\n"
                 f"<b>✅ To'g'ri Javoblar: {count} ta</b>\n"
                 f"<b>❌ Noto'g'ri javoblar: {fail} ta</b>\n"
                 f"<b>✖️ Javob berilmaganlari: {size - count - fail} ta</b>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return
    elif message.text == enw[0]:
        count += 1
        await state.update_data(count=count)
    else:
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(f"💡: ☑️{enw[0]}")
        fail += 1
        await state.update_data(fail=fail)
    if uz_words:
        uz = choice(uz_words)
        en_word = db.get_en_from_uz(uz=uz[0])
        en_words.remove(en_word)
        await message.answer(
            text=f"<b>{uz[0]}</b>",
            reply_markup=select_word_kb(sample(en_words, k=3) + [en_word])
        )
        uz_words.remove(uz)
        await state.update_data(uz_words=uz_words)
        await state.update_data(en_words=db.get_en_all())
        await state.update_data(en_word=en_word)
    else:
        await message.answer("Ushbu toifadagi so'zlarni tugatdingiz🎉")
        await message.answer(
            text=f"<b>📊 Natijangiz:</b>\n\n"
                 f"<b>🔢 Jami so'zlar {size} ta</b>\n"
                 f"<b>✅ To'g'ri Javoblar: {count} ta</b>\n"
                 f"<b>❌ Noto'g'ri javoblar: {fail} ta</b>\n"
                 f"<b>✖️ Javob berilmaganlari: {size - count - fail} ta</b>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()

@word_router.message(Command('ru_uz_quiz'))
async def ru_uz_quiz_handler(message: Message, state: FSMContext):
    global succ, faild
    succ, faild = 0, 0
    await state.set_state(Quiz.quizCategory)
    await state.update_data(txt='.')
    await message.answer(
        text="Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(Quiz.quizCategory)
async def ruuz_word_handler(call: CallbackQuery, state: FSMContext):
    name = db.get_category_name(id=call.data)
    ru_words = db.get_uz_words(id=call.data)
    if ru_words:
        await call.message.delete()
        await state.set_state(Quiz.quizNext)
        await call.message.answer(
            text=f"<b>{name.upper()}</b> toifasidan qaysi oraliqdagi testlarni yechmoqchisiz?\n\n"
                 f"<i>Pastdagi tugmalar orqali tanlashingiz mumkin⬇️</i>",
            reply_markup=between_keyboard(id=call.data)
        )
    else:
        await call.answer("📥Bu toifa bo'sh boshqa toifani tanlang🔄", show_alert=True)
    await state.update_data(txt='.')
    await state.update_data(id=call.data)


@word_router.message(Quiz.quizNext)
async def ruuz_quiz_handler(message: Message, state: FSMContext):
    global sleep_task, quiz_answer, succ, faild, num, flag
    all = await state.get_data()
    try:
        between = message.text.split('-')
        name = db.get_category_name(id=all['id'])
        ru_words = db.get_ru_words(id=all['id'])[int(between[0]) - 1:int(between[1])]
        num = len(ru_words)
    except ValueError:
        if message.text == 'Tugatish✖':
            await message.answer(
                text=f"<b>📊 Natijangiz:</b>\n\n"
                     f"<b>🔢 Jami so'zlar {num} ta</b>\n"
                     f"<b>✅ To'g'ri Javoblar: {succ} ta</b>\n"
                     f"<b>❌ Noto'g'ri javoblar: {faild} ta</b>\n"
                     f"<b>✖️ Javob berilmaganlari: {num - succ - faild} ta</b>",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            flag = True
        else:
            await message.reply("<i>Pastdagi tugmalar orqali tanlang</i>👇")
    try:
        if ru_words:
            await message.answer(
                text=f"Yaxshi, {message.text} oraliqda <b>{name}</b> toifasidan men <b>Ruschasini</b> beraman siz <b>O'zbekchasini</b> topasiz\n🇷🇺 🔁 ➡️ 🇺🇿",
                reply_markup=ReplyKeyboardRemove()
            )
            await asyncio.sleep(3)
            msg = await message.answer(text="🤖Tayyormisiz? 3️⃣")
            await asyncio.sleep(1)
            for text in ["⚡️Boshlanmoqda 2️⃣...", "🚀Kettik 1️⃣"]:
                await msg.edit_text(
                    text=text
                )
                await asyncio.sleep(1)
            await msg.delete()
            shuffle(ru_words)
            for ru in ru_words:
                if not flag:
                    uz_words = db.get_uz_all()
                    uz_word = db.get_uz_from_ru(ru=ru[0])
                    uz_words.remove(uz_word)

                    words_ls = [i[0] for i in [uz_word] + sample(uz_words, k=3)]
                    question = f"<b>{ru[0].upper()}</b>"
                    shuffle(words_ls)
                    correct_option_id = words_ls.index(uz_word[0])

                    poll = await message.answer_poll(
                        question=question,
                        options=words_ls,
                        type=PollType.QUIZ,
                        correct_option_id=correct_option_id,
                        is_anonymous=False,
                        explanation=f"{ru[0]} - {uz_word[0]}",
                        open_period=10,
                        reply_markup=quiz_stop
                    )

                    quiz_answer[poll.poll.id] = poll.poll.correct_option_id
                    sleep_task = asyncio.create_task(asyncio.sleep(11))

                    try:
                        await sleep_task
                    except asyncio.CancelledError:
                        await asyncio.sleep(0.5)
                else:
                    break

            if not flag:
                await message.answer("Ushbu toifadagi so'zlarni tugatdingiz🎉")
                await message.answer(
                    text=f"<b>📊 Natijangiz:</b>\n\n"
                         f"<b>🔢 Jami so'zlar {num} ta</b>\n"
                         f"<b>✅ To'g'ri Javoblar: {succ} ta</b>\n"
                         f"<b>❌ Noto'g'ri javoblar: {faild} ta</b>\n"
                         f"<b>✖️ Javob berilmaganlari: {num - succ - faild} ta</b>",
                    reply_markup=ReplyKeyboardRemove()
                )
                await state.clear()
            flag = False
        else:
            txt = all['txt']
            await message.edit_text(
                text=f"Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇{txt}",
                reply_markup=get_categories_kb()
            )
            await state.update_data(txt=txt + '.')
    except:
        pass


@word_router.message(Command('uz_ru_quiz'))
async def uz_ru_quiz_handler(message: Message, state: FSMContext):
    global succ, faild
    succ, faild = 0, 0
    await state.set_state(QuizUzRu.quizCategory)
    await state.update_data(txt='.')
    await message.answer(
        text="Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(QuizUzRu.quizCategory)
async def uzru_quiz_handler(call: CallbackQuery, state: FSMContext):
    name = db.get_category_name(id=call.data)
    ru_words = db.get_ru_words(id=call.data)
    if ru_words:
        await call.message.delete()
        await state.set_state(QuizUzRu.quizNext)
        await call.message.answer(
            text=f"<b>{name.upper()}</b> toifasidan qaysi oraliqdagi testlarni yechmoqchisiz?\n\n"
                 f"<i>Pastdagi tugmalar orqali tanlashingiz mumkin⬇️</i>",
            reply_markup=between_keyboard(id=call.data)
        )
    else:
        await call.answer("📥Bu toifa bo'sh boshqa toifani tanlang🔄", show_alert=True)
    await state.update_data(txt='.')
    await state.update_data(id=call.data)


@word_router.message(QuizUzRu.quizNext)
async def uzru_quiz_handler(message: Message, state: FSMContext):
    global sleep_task, quiz_answer, succ, faild, num, flag
    all = await state.get_data()
    try:
        between = message.text.split('-')
        name = db.get_category_name(id=all['id'])
        uz_words = db.get_uz_words(id=all['id'])[int(between[0]) - 1:int(between[1])]
        num = len(uz_words)
    except ValueError:
        if message.text == 'Tugatish✖':
            await message.answer(
                text=f"<b>📊 Natijangiz:</b>\n\n"
                     f"<b>🔢 Jami so'zlar {num} ta</b>\n"
                     f"<b>✅ To'g'ri Javoblar: {succ} ta</b>\n"
                     f"<b>❌ Noto'g'ri javoblar: {faild} ta</b>\n"
                     f"<b>✖️ Javob berilmaganlari: {num - succ - faild} ta</b>",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            flag = True
        else:
            await message.reply("<i>Pastdagi tugmalar orqali tanlang</i>👇")
    try:
        if uz_words:
            await message.answer(
                text=f"Yaxshi, {message.text} oraliqda <b>{name}</b> toifasidan men <b>Ruschasini</b> beraman siz <b>O'zbekchasini</b> topasiz\n🇷🇺 🔁 ➡️ 🇺🇿",
                reply_markup=ReplyKeyboardRemove()
            )
            await asyncio.sleep(3)
            msg = await message.answer(text="🤖Tayyormisiz? 3️⃣")
            await asyncio.sleep(1)
            for text in ["⚡️Boshlanmoqda 2️⃣...", "🚀Kettik 1️⃣"]:
                await msg.edit_text(
                    text=text
                )
                await asyncio.sleep(1)
            await msg.delete()
            shuffle(uz_words)
            for uz in uz_words:
                if not flag:
                    ru_words = db.get_ru_all()
                    ru_word = db.get_ru_from_uz(uz=uz[0])
                    ru_words.remove(ru_word)

                    words_ls = [i[0] for i in [ru_word] + sample(ru_words, k=3)]
                    question = f"<b>{uz[0].upper()}</b>"
                    shuffle(words_ls)
                    correct_option_id = words_ls.index(ru_word[0])

                    poll = await message.answer_poll(
                        question=question,
                        options=words_ls,
                        type=PollType.QUIZ,
                        correct_option_id=correct_option_id,
                        is_anonymous=False,
                        explanation=f"{uz[0]} - {ru_word[0]}",
                        open_period=10,
                        reply_markup=quiz_stop
                    )

                    quiz_answer[poll.poll.id] = poll.poll.correct_option_id
                    sleep_task = asyncio.create_task(asyncio.sleep(11))

                    try:
                        await sleep_task
                    except asyncio.CancelledError:
                        await asyncio.sleep(0.5)
                else:
                    break

            if not flag:
                await message.answer("Ushbu toifadagi so'zlarni tugatdingiz🎉")
                await message.answer(
                    text=f"<b>📊 Natijangiz:</b>\n\n"
                         f"<b>🔢 Jami so'zlar {num} ta</b>\n"
                         f"<b>✅ To'g'ri Javoblar: {succ} ta</b>\n"
                         f"<b>❌ Noto'g'ri javoblar: {faild} ta</b>\n"
                         f"<b>✖️ Javob berilmaganlari: {num - succ - faild} ta</b>",
                    reply_markup=ReplyKeyboardRemove()
                )
                await state.clear()
            flag = False
        else:
            txt = all['txt']
            await message.edit_text(
                text=f"Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇{txt}",
                reply_markup=get_categories_kb()
            )
            await state.update_data(txt=txt + '.')
    except:
        pass

@word_router.message(Command('en_uz_quiz'))
async def en_uz_quiz_handler(message: Message, state: FSMContext):
    global succ, faild
    succ, faild = 0, 0
    await state.set_state(QuizEnUz.quizCategory)
    await state.update_data(txt='.')
    await message.answer(
        text="Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(QuizEnUz.quizCategory)
async def enuz_quiz_handler(call: CallbackQuery, state: FSMContext):
    name = db.get_category_name(id=call.data)
    en_words = db.get_en_words(id=call.data)
    if en_words:
        await call.message.delete()
        await state.set_state(QuizEnUz.quizNext)
        await call.message.answer(
            text=f"<b>{name.upper()}</b> toifasidan qaysi oraliqdagi testlarni yechmoqchisiz?\n\n"
                 f"<i>Pastdagi tugmalar orqali tanlashingiz mumkin⬇️</i>",
            reply_markup=between_keyboard(id=call.data)
        )
    else:
        await call.answer("📥Bu toifa bo'sh boshqa toifani tanlang🔄", show_alert=True)
    await state.update_data(txt='.')
    await state.update_data(id=call.data)


@word_router.message(QuizEnUz.quizNext)
async def enuz_word_handler(message: Message, state: FSMContext):
    global sleep_task, quiz_answer, succ, faild, num, flag
    all = await state.get_data()
    try:
        between = message.text.split('-')
        name = db.get_category_name(id=all['id'])
        en_words = db.get_en_words(id=all['id'])[int(between[0]) - 1:int(between[1])]
        num = len(en_words)
    except ValueError:
        if message.text == 'Tugatish✖':
            await message.answer(
                text=f"<b>📊 Natijangiz:</b>\n\n"
                     f"<b>🔢 Jami so'zlar {num} ta</b>\n"
                     f"<b>✅ To'g'ri Javoblar: {succ} ta</b>\n"
                     f"<b>❌ Noto'g'ri javoblar: {faild} ta</b>\n"
                     f"<b>✖️ Javob berilmaganlari: {num - succ - faild} ta</b>",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            flag = True
        else:
            await message.reply("<i>Pastdagi tugmalar orqali tanlang</i>👇")
    try:
        if en_words:
            await message.answer(
                text=f"Yaxshi, {message.text} oraliqda <b>{name}</b> toifasidan men <b>Inglizchasini</b> beraman siz <b>O'zbekchasini</b> topasiz\n🇺🇸 🔁 ➡️ 🇺🇿",
                reply_markup=ReplyKeyboardRemove()
            )
            await asyncio.sleep(3)
            msg = await message.answer(text="🤖Tayyormisiz? 3️⃣")
            await asyncio.sleep(1)
            for text in ["⚡️Boshlanmoqda 2️⃣...", "🚀Kettik 1️⃣"]:
                await msg.edit_text(
                    text=text
                )
                await asyncio.sleep(1)
            await msg.delete()
            shuffle(en_words)
            for en in en_words:
                if not flag:
                    uz_words = db.get_uz_all()
                    uz_word = db.get_uz_from_en(en=en[0])
                    uz_words.remove(uz_word)

                    words_ls = [i[0] for i in [uz_word] + sample(uz_words, k=3)]
                    question = f"<b>{en[0].upper()}</b>"
                    shuffle(words_ls)
                    correct_option_id = words_ls.index(uz_word[0])

                    poll = await message.answer_poll(
                        question=question,
                        options=words_ls,
                        type=PollType.QUIZ,
                        correct_option_id=correct_option_id,
                        is_anonymous=False,
                        explanation=f"{en[0]} - {uz_word[0]}",
                        open_period=10,
                        reply_markup=quiz_stop
                    )

                    quiz_answer[poll.poll.id] = poll.poll.correct_option_id
                    sleep_task = asyncio.create_task(asyncio.sleep(11))

                    try:
                        await sleep_task
                    except asyncio.CancelledError:
                        await asyncio.sleep(0.5)
                else:
                    break

            if not flag:
                await message.answer("Ushbu toifadagi so'zlarni tugatdingiz🎉")
                await message.answer(
                    text=f"<b>📊 Natijangiz:</b>\n\n"
                         f"<b>🔢 Jami so'zlar {num} ta</b>\n"
                         f"<b>✅ To'g'ri Javoblar: {succ} ta</b>\n"
                         f"<b>❌ Noto'g'ri javoblar: {faild} ta</b>\n"
                         f"<b>✖️ Javob berilmaganlari: {num - succ - faild} ta</b>",
                    reply_markup=ReplyKeyboardRemove()
                )
                await state.clear()
            flag = False
        else:
            txt = all['txt']
            await message.edit_text(
                text=f"Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇{txt}",
                reply_markup=get_categories_kb()
            )
            await state.update_data(txt=txt + '.')
    except:
        pass



@word_router.message(Command('uz_en_quiz'))
async def uz_en_quiz_handler(message: Message, state: FSMContext):
    global succ, faild
    succ, faild = 0, 0
    await state.set_state(QuizUzEn.quizCategory)
    await state.update_data(txt='.')
    await message.answer(
        text="Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇",
        reply_markup=get_categories_kb()
    )

@word_router.callback_query(QuizUzEn.quizCategory)
async def enuz_quiz_handler(call: CallbackQuery, state: FSMContext):
    name = db.get_category_name(id=call.data)
    uz_words = db.get_uz_words(id=call.data)
    if uz_words:
        await call.message.delete()
        await state.set_state(QuizUzEn.quizNext)
        await call.message.answer(
            text=f"<b>{name.upper()}</b> toifasidan qaysi oraliqdagi testlarni yechmoqchisiz?\n\n"
                 f"<i>Pastdagi tugmalar orqali tanlashingiz mumkin⬇️</i>",
            reply_markup=between_keyboard(id=call.data)
        )
    else:
        await call.answer("📥Bu toifa bo'sh boshqa toifani tanlang🔄", show_alert=True)
    await state.update_data(txt='.')
    await state.update_data(id=call.data)


@word_router.message(QuizUzEn.quizNext)
async def uzen_word_handler(message: Message, state: FSMContext):
    global sleep_task, quiz_answer, succ, faild, num, flag
    all = await state.get_data()
    try:
        between = message.text.split('-')
        name = db.get_category_name(id=all['id'])
        uz_words = db.get_uz_words(id=all['id'])[int(between[0]) - 1:int(between[1])]
        num = len(uz_words)
    except ValueError:
        if message.text == 'Tugatish✖':
            await message.answer(
                text=f"<b>📊 Natijangiz:</b>\n\n"
                     f"<b>🔢 Jami so'zlar {num} ta</b>\n"
                     f"<b>✅ To'g'ri Javoblar: {succ} ta</b>\n"
                     f"<b>❌ Noto'g'ri javoblar: {faild} ta</b>\n"
                     f"<b>✖️ Javob berilmaganlari: {num - succ - faild} ta</b>",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            flag = True
        else:
            await message.reply("<i>Pastdagi tugmalar orqali tanlang</i>👇")
    try:
        if uz_words:
            await message.answer(
                text=f"Yaxshi, {message.text} oraliqda <b>{name}</b> toifasidan men <b>O'zbekchasini</b> beraman siz <b>Inglizchasini</b> topasiz\n🇺🇿 🔁 ➡️ 🇺🇸",
                reply_markup=ReplyKeyboardRemove()
            )
            await asyncio.sleep(3)
            msg = await message.answer(text="🤖Tayyormisiz? 3️⃣")
            await asyncio.sleep(1)
            for text in ["⚡️Boshlanmoqda 2️⃣...", "🚀Kettik 1️⃣"]:
                await msg.edit_text(
                    text=text
                )
                await asyncio.sleep(1)
            await msg.delete()
            shuffle(uz_words)
            for uz in uz_words:
                if not flag:
                    en_words = db.get_en_all()
                    en_word = db.get_en_from_uz(uz=uz[0])
                    en_words.remove(en_word)

                    words_ls = [i[0] for i in [en_word] + sample(en_words, k=3)]
                    question = f"<b>{uz[0].upper()}</b>"
                    shuffle(words_ls)
                    correct_option_id = words_ls.index(en_word[0])

                    poll = await message.answer_poll(
                        question=question,
                        options=words_ls,
                        type=PollType.QUIZ,
                        correct_option_id=correct_option_id,
                        is_anonymous=False,
                        explanation=f"{uz[0]} - {en_word[0]}",
                        open_period=10,
                        reply_markup=quiz_stop
                    )

                    quiz_answer[poll.poll.id] = poll.poll.correct_option_id
                    sleep_task = asyncio.create_task(asyncio.sleep(11))

                    try:
                        await sleep_task
                    except asyncio.CancelledError:
                        await asyncio.sleep(0.5)
                else:
                    break

            if not flag:
                await message.answer("Ushbu toifadagi so'zlarni tugatdingiz🎉")
                await message.answer(
                    text=f"<b>📊 Natijangiz:</b>\n\n"
                         f"<b>🔢 Jami so'zlar {num} ta</b>\n"
                         f"<b>✅ To'g'ri Javoblar: {succ} ta</b>\n"
                         f"<b>❌ Noto'g'ri javoblar: {faild} ta</b>\n"
                         f"<b>✖️ Javob berilmaganlari: {num - succ - faild} ta</b>",
                    reply_markup=ReplyKeyboardRemove()
                )
                await state.clear()
            flag = False
        else:
            txt = all['txt']
            await message.edit_text(
                text=f"Qaysi toifa so'zlarini yod olmoqchsiz, tanlang👇{txt}",
                reply_markup=get_categories_kb()
            )
            await state.update_data(txt=txt + '.')
    except:
        pass

@word_router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer):
    global sleep_task, quiz_answer, succ, faild
    if quiz_answer[poll_answer.poll_id] == poll_answer.option_ids[0]:
        succ += 1
    else:
        faild += 1
    if not sleep_task.done():
        sleep_task.cancel()
    quiz_answer.clear()

@word_router.message(Command('bas'))
async def bass_handler(message: Message):
    await message.answer_dice(emoji="🏀")

@word_router.message(Command('dic'))
async def send_dice(message: Message):
    await message.answer_dice()

@word_router.message(Command('dart'))
async def send_dart(message: Message):
    await message.answer_dice(emoji="🎯")