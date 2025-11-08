from aiogram.types import BotCommand

admin_commands = [
    BotCommand(command='start', description="Botni ishga tushirish"),
    BotCommand(command='uz_ru_select', description="O'zbekchadan Ruschani topish"),
    BotCommand(command='ru_uz_select', description="Ruschadan O'zbekchani topish"),
    BotCommand(command='uz_en_select', description="O'zbekchadan Inglizchani topish"),
    BotCommand(command='en_uz_select', description="Inglizchadan O'zbekchani topish"),
    BotCommand(command='uz_ru_quiz', description="🇺🇿 ➡️ 🇷🇺"),
    BotCommand(command='ru_uz_quiz', description="🇷🇺 ➡️ 🇺🇿"),
    BotCommand(command='uz_en_quiz', description="🇺🇿 ➡️ 🇺🇸"),
    BotCommand(command='en_uz_quiz', description="🇺🇸 ➡️ 🇺🇿"),
    # BotCommand(command='uz_ru_translate', description="O'zbekdan Rusga"),
    # BotCommand(command='ru_uz_translate', description="Rusdan O'zbekga"),
    BotCommand(command='words', description="So'zlarni ko'rish"),
    BotCommand(command='categories', description="Mavjud toifalar"),
    BotCommand(command='add_category', description='Toifa qo\'shish'),
    BotCommand(command='edit_category', description='Toifani o\'zgartirish'),
    BotCommand(command='delete_category', description='Toifani o\'chirish'),
    BotCommand(command='new_word_add', description="Yangi so'z qo'shish"),
    BotCommand(command='new_words_excel', description="Yangi so'zlar qo'shish excelda"),
    BotCommand(command='cancel', description="Jarayonni to'xtatish"),
    BotCommand(command='help', description="Bot haqida batafsil ma'lumot"),
]

user_commands = [
    BotCommand(command='start', description="Botni ishga tushirish"),
    BotCommand(command='words', description="So'zlarni ko'rish"),
    BotCommand(command='uz_ru_select', description="🇺🇿 ➡️ 🇷🇺"),
    BotCommand(command='ru_uz_select', description="🇷🇺 ➡️ 🇺🇿"),
    BotCommand(command='uz_en_select', description="🇺🇿 ➡️ 🇺🇸"),
    BotCommand(command='en_uz_select', description="🇺🇸 ➡️ 🇺🇿"),
    BotCommand(command='uz_ru_quiz', description="🇺🇿 ➡️ 🇷🇺"),
    BotCommand(command='ru_uz_quiz', description="🇷🇺 ➡️ 🇺🇿"),
    BotCommand(command='uz_en_quiz', description="🇺🇿 ➡️ 🇺🇸"),
    BotCommand(command='en_uz_quiz', description="🇺🇸 ➡️ 🇺🇿"),
    BotCommand(command='help', description="Bot haqida batafsil ma'lumot"),
]