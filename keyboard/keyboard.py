from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.database import Database
from config import DB_NAME

from random import shuffle

db = Database(DB_NAME)

off = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Tugatish')],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

quiz_stop = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Tugatish✖')],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

def select_word_kb(words):
    row = []
    shuffle(words)
    row.append([KeyboardButton(text=words[0][0]), KeyboardButton(text=words[1][0])])
    row.append([KeyboardButton(text=words[2][0]), KeyboardButton(text=words[3][0])])
    row.append([KeyboardButton(text="Tugatish✖")])

    select_kb = ReplyKeyboardMarkup(
        keyboard=row,
    resize_keyboard=True,
    )
    return select_kb


def between_keyboard(id):
    words = db.get_words_category(category_id=id)
    words_between_kb = ReplyKeyboardBuilder()
    for i in range(0, len(words), 10):
        words_between_kb.button(text=f"{i+1}-{i+10}")

    words_between_kb.adjust(4)
    words_between_kb = words_between_kb.as_markup(resize_keyboard=True, one_time_keyboard=True)
    return words_between_kb