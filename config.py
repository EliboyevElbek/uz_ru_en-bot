from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PASS = os.getenv("DB_PASS")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

big_admin = int(os.getenv("big_admin"))


admin_commands_dict = {
'/uz_ru_select':"O'zbekchadan Ruschani topish",
'/ru_uz_select':"Ruschadan O'zbekchani topish",
'/uz_en_select':"O'zbekchadan Inglizchani topish",
'/en_uz_select':"Inglizchadan O'zbekchani topish",
'/uz_ru_quiz': "🇺🇿 ➡️ 🇷🇺",
'/ru_uz_quiz':"🇷🇺 ➡️ 🇺🇿",
'/uz_en_quiz':"🇺🇿 ➡️ 🇺🇸",
'/en_uz_quiz':"🇺🇸 ➡️ 🇺🇿",
'/add_category':'Toifa qo\'shish',
'/edit_category':'Toifani o\'zgartirish',
'/delete_category':'Toifani o\'chirish',
'/new_word_add':"Yangi so'z qo'shish",
'/new_words_excel':"Yangi so'zlar qo'shish excelda",
}

user_commands_dict = {
'/uz_ru_select':"🇺🇿 ➡️ 🇷🇺",
'/ru_uz_select':"🇷🇺 ➡️ 🇺🇿",
'/uz_en_select':"🇺🇿 ➡️ 🇺🇸",
'/en_uz_select':"🇺🇸 ➡️ 🇺🇿",
'/uz_ru_quiz':"🇺🇿 ➡️ 🇷🇺",
'/ru_uz_quiz':"🇷🇺 ➡️ 🇺🇿",
'/uz_en_quiz':"🇺🇿 ➡️ 🇺🇸",
'/en_uz_quiz':"🇺🇸 ➡️ 🇺🇿",
}