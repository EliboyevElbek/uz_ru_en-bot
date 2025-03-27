from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


from utils.database import Database
from config import DB_NAME, big_admin
from state.admin_state import CategoryState
from keyboard.inline_keyboard import get_categories_kb, confirm

category_router = Router()
db = Database(DB_NAME)


@category_router.message(Command('categories'))
async def get_categories(message: Message):
    if message.from_user.id == big_admin:
        info = 'Sizda mavjud barcha toifalar\n\n'
        cts = [cat[1] for cat in db.get_categories()]
        count = 0
        for ct in cts:
            count += 1
            info += f"👉{count}. <b>{ct.upper()}</b>\n\n"
        await message.answer(info)
    else:
        await message.reply("Siz uchun mavjud bo'lmagan buyruqlarni yozmang!🙂")

@category_router.message(Command('add_category'), F.chat.id == big_admin)
async def add_category(message: Message, state: FSMContext):
    await state.set_state(CategoryState.addCategory)
    await message.answer('🆕 Yangi toifa uchun nom kiriting')

@category_router.message(CategoryState.addCategory)
async def add_category_done(message: Message, state: FSMContext):
    if db.check_category(message.text.lower()):
        if db.add_category(message.text.lower()):
            await state.clear()
            await message.answer(f'✅<b>{message.text.upper()}</b> toifasi muvaffaqiyatli qo\'shildi')
        else:
            await message.answer('❌Xato!, yangi toifa qo\'shishda xatolik')
    else:
        await message.answer('❎Bu toifa allaqchon mavjud, boshqa nom kiriting yoki \n/cancel bosib jarayonni bekor qiling.')

@category_router.message(Command('edit_category'), F.chat.id == big_admin)
async def edit_category(message: Message, state: FSMContext):
    await state.set_state(CategoryState.editCategorySelect)
    await message.answer(
        text="O'zgartirmoqchi bo'lgan toifangizni tanlang👇",
        reply_markup=get_categories_kb()
    )

@category_router.callback_query(CategoryState.editCategorySelect)
async def edit_category_name(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cat_name=callback.data)
    await state.set_state(CategoryState.editCategoryName)
    await callback.message.edit_text(
        f"📝<b>{callback.data.upper()}</b> toifasi uchun yangi o'zgartirmoqchi bo'lgan nomingizni kiriting"
    )

@category_router.message(CategoryState.editCategoryName)
async def edit_category_done(message: Message, state: FSMContext):
    if db.check_category(message.text):
        all_data = await state.get_data()
        if db.edit_category(old=all_data.get('cat_name'), new=message.text):
            await state.clear()
            await message.answer(
                f"✅<b>{all_data.get('cat_name').upper()}</b> toifasi <b>{message.text.upper()}</b> toifaga muvaffaqiyatli o'zgartirildi")
        else:
            await message.answer('❌Xatolik yuz berdi qayta urinib ko\'ring')
    else:
        await message.answer(
            '❎Bu toifa allaqchon mavjud, boshqa nom kiriting yoki \n/cancel bosib jarayonni bekor qiling.')

@category_router.message(Command('delete_category'), F.chat.id == big_admin)
async def delete_category(message: Message, state: FSMContext):
    await state.set_state(CategoryState.startDelete)
    await message.answer(text="🗑O'chirmoqchi bo'lgan toifani tanlang", reply_markup=get_categories_kb())

@category_router.callback_query(CategoryState.startDelete)
async def delete_confirm_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CategoryState.finishDelete)
    cat_name = db.get_category_name(id=callback.data)
    await state.update_data(toifa=cat_name.lower())
    await callback.message.edit_text(f"<b>{cat_name}</b> toifasi rostan ham o'chirilsinmi", reply_markup=confirm)

@category_router.callback_query(CategoryState.finishDelete)
async def delete_complete_category(callback: CallbackQuery, state: FSMContext):
    info = await state.get_data()
    if callback.data == 'yes':
        if db.delete_category(info.get('toifa')):
            await state.clear()
            await callback.message.delete()
            await callback.message.answer(f"☑️<b>{info.get('toifa').upper()}</b> toifasi o'chirildi")
        else:
            await callback.message.delete()
            await callback.message.answer("✖️Xatolik yuz berdi")
    else:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer("↪️O'chirish bekor qilindi")