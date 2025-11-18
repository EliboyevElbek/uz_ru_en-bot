import time

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeChat

from config import big_admin
from utils.commands import admin_commands, user_commands
from utils.database import Database
from config import DB_NAME, admin_commands_dict, user_commands_dict

db = Database(DB_NAME)
command_router = Router()

@command_router.message(CommandStart(), F.chat.id == big_admin)
async def start_admin_handler(message: Message):
    await message.bot.set_my_commands(admin_commands,
        scope=BotCommandScopeChat(chat_id=message.chat.id)
    )
    await message.answer(
        f"✅Admin botga xush kelibsiz! {message.from_user.mention_html(message.from_user.full_name)}"
    )

@command_router.message(CommandStart())
async def start_user_handler(message: Message):
    await message.bot.set_my_commands(
        user_commands,
        scope=BotCommandScopeChat(chat_id=message.chat.id)
    )
    db.bot_members(tg_id=message.from_user.id, username=message.from_user.username, full_name=message.from_user.full_name)
    await message.answer(
        f"🤖Botga xush kelibsiz! {message.from_user.mention_html(message.from_user.full_name)}"
    )

@command_router.message(Command('help'))
async def help_handler(message: Message):
    await message.reply(
        text=f"🚨Hurmatli {message.from_user.mention_html(message.from_user.full_name)}!\n"
             f"bu botda siz <b>Rus tilida</b> so'z yodlashni yanada osonlashtirishingiz mumkin.\n\n"
             f"<b>Buyruqlar:</b>\n<b>uz-ru-select</b> - O'zbekcha so'z va ruschada 4 ta varianti beriladi siz"
             f" to'g'risini topishingiz kerak bo'ladi.\n\n<b>ru-uz-select</b> - bu tepadagi buyruqni aksi"
             f" Ruscha so'z va o'zbekchada 4 ta varianti beriladi to'g'risini topishingiz kerak.\n\n"
             f" <b>uz_ru_quiz</b> - <b>ru_uz_quiz</b> - <b>uz_en_quiz</b> - <b>en_uz_quiz</b> bular huddi tepadagi"
             f" buyruqlarga mos ravishda quizlari.\n\n"
             f"<b>uz-ru-typing</b> - bu buyruqda O'zbekchada so'z beriladi siz ruschasini imlo xatosiz yozishingiz kerak. (<i>Tez orada...🔜</i>)\n\n"
             f"<b>ru-uz-typing</b> - bu tepadagini aksi Ruschada so'z beriladi O'zbekchasini yozasiz. (<i>Tez orada...🔜</i>)\n\n\n"
             f"<i>Tepadagilardan birortasini tanlang🙂</i>"
    )

@command_router.message(Command('commands'), F.chat.id == big_admin)
async def admin_commands_handler(message: Message):
    info = ''
    for key, value in admin_commands_dict.items():
        info += f"<b>{key}</b> - {value}\n\n"
    msg = await message.answer(info)
    time.sleep(6)
    await msg.delete()

@command_router.message(Command('commands'))
async def user_commands_handler(message: Message):
    info = ''
    for key, value in user_commands_dict.items():
        info += f"<b>{key}</b> - {value}\n\n"
    msg = await message.answer(info)
    time.sleep(6)
    await msg.delete()

@command_router.message(Command('cancel'))
async def cansel_handler(message: Message, state: FSMContext):
    now_state = await state.get_state()
    if now_state is None:
        await message.reply("🚫To'xtatishga hech qanday jarayon mavjud emas")
    else:
        await state.clear()
        await message.reply('⛔️Jarayon bekor qilindi.')