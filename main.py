import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from handlers.category_handler import category_router
from handlers.command_handler import command_router
from handlers.listening_handler import listen_router
from handlers.words_handler import word_router
from handlers.added_handler import added_router

from config import BOT_TOKEN

dp = Dispatcher()

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp.include_routers(
        category_router,
        command_router,
        word_router,
        added_router,
        listen_router
    )
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtadi")

