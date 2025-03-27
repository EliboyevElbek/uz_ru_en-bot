from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.database import Database
from config import DB_NAME

db = Database(DB_NAME)

def get_categories_kb():
    row = []
    categories = db.get_categories()
    for category in categories:
        row.append(
            [InlineKeyboardButton(text=category[1], callback_data=str(category[0]))]
        )

    cat_kb = InlineKeyboardMarkup(
        inline_keyboard=row
    )
    return cat_kb

confirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='HA', callback_data='yes'),
            InlineKeyboardButton(text='YO\'Q', callback_data='no'),
        ]
    ]
)

select_lang = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿O'zbekcha", callback_data='uz'),
            InlineKeyboardButton(text="🇷🇺Ruscha", callback_data='ru'),
        ]
    ]
)

def between_kb(words10, l=0):
    row = []
    if l + 1 == words10 and words10 > 1:
        row.append([InlineKeyboardButton(text='⬅️', callback_data='prev'),
                    InlineKeyboardButton(text='🇷🇺🔁🇺🇸', callback_data='en')])
    elif words10 > 1 and l > 0:
        row.append([InlineKeyboardButton(text='⬅️', callback_data='prev'),
                    InlineKeyboardButton(text='🇷🇺🔁🇺🇸', callback_data='en'),
                   InlineKeyboardButton(text='➡️', callback_data='next')])
    elif words10 > 1:
        row.append([InlineKeyboardButton(text='➡️', callback_data='next'),
                    InlineKeyboardButton(text='🇷🇺🔁🇺🇸', callback_data='en')])

    b_kb = InlineKeyboardMarkup(
        inline_keyboard=row
    )
    return b_kb

def between_kb_en(words10, l=0):
    row = []
    if l + 1 == words10 and words10 > 1:
        row.append([InlineKeyboardButton(text='⬅️', callback_data='prev'),
                    InlineKeyboardButton(text='🇺🇸🔁🇷🇺', callback_data='uz')])
    elif words10 > 1 and l > 0:
        row.append([InlineKeyboardButton(text='⬅️', callback_data='prev'),
                    InlineKeyboardButton(text='🇺🇸🔁🇷🇺', callback_data='uz'),
                   InlineKeyboardButton(text='➡️', callback_data='next')])
    elif words10 > 1:
        row.append([InlineKeyboardButton(text='➡️', callback_data='next'),
                    InlineKeyboardButton(text='🇺🇸🔁🇷🇺', callback_data='uz')])

    b_kb_en = InlineKeyboardMarkup(
        inline_keyboard=row
    )
    return b_kb_en

def sura_kb(count=0):
    row = []
    if 0 < count < 9:
        row.append([InlineKeyboardButton(text='⬅️', callback_data='prev'),
                    InlineKeyboardButton(text='❌', callback_data='del'),
                    InlineKeyboardButton(text='➡️', callback_data='next')])
    elif count == 9:
        row.append(
            [InlineKeyboardButton(text='⬅️', callback_data='prev'),
             InlineKeyboardButton(text='❌', callback_data='del')]
        )
    else:
        row.append(
            [InlineKeyboardButton(text='❌', callback_data='del'),
            InlineKeyboardButton(text='➡️', callback_data='next')]
        )
    row.append([InlineKeyboardButton(text='Tahrirlash', callback_data='edit')])
    sura_kb_bt = InlineKeyboardMarkup(
        inline_keyboard=row
    )
    return sura_kb_bt