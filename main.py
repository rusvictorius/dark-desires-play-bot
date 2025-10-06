import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# ======================
# ENV & Bot
# ======================
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ======================
# FastAPI app
# ======================
app = FastAPI()

@app.get("/")
async def health():
    return {"status": "ok", "bot": "Dark Desires Play"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
    print("🤖 Dark Desires Play Bot запущен...")


# ======================
# FSM (регистрация)
# ======================
class Register(StatesGroup):
    gender = State()
    search_for = State()
    city = State()
    about = State()

user_profiles = {}

# ======================
# Инлайн-кнопки
# ======================
def kb_start():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚡ ВОЙТИ НА ТЁМНУЮ СТОРОНУ ⚡", callback_data="enter_dark_side")]
        ]
    )

def kb_age():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Мне 18", callback_data="confirm_18")]
        ]
    )

def kb_rules():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔥 Я даю согласие и принимаю правила 🔥", callback_data="accept_rules")]
        ]
    )

def kb_gender():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Мужчина", callback_data="gender_m"),
                InlineKeyboardButton(text="👩 Женщина", callback_data="gender_f"),
                InlineKeyboardButton(text="🌈 Другое", callback_data="gender_o")
            ]
        ]
    )

def kb_search_for():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👩 Женщин", callback_data="search_f"),
                InlineKeyboardButton(text="👨 Мужчин", callback_data="search_m"),
                InlineKeyboardButton(text="🔥 Все варианты", callback_data="search_a")
            ]
        ]
    )

# ======================
# Обработчики
# ======================

@dp.message(CommandStart())
async def start(message: types.Message):
    text = (
        "🖤 <b>DARK DESIRES PLAY</b> 🔥\n\n"
        "Только для взрослых.\n"
        "Без имён. Без масок. Без обязательств.\n\n"
        "<i>Ты готов войти?</i>"
    )
    await message.answer(text, reply_markup=kb_start())


@dp.callback_query(F.data == "enter_dark_side")
async def enter_dark_side(callback: types.CallbackQuery):
    text = (
        "🌒 <b>ТЁМНАЯ СТОРОНА НЕ ДЛЯ ВСЕХ</b> 🌒\n\n"
        "Продолжая, ты подтверждаешь, что тебе уже есть 18 лет\n"
        "и ты находишься в здравом уме и памяти."
    )
    await callback.message.edit_text(text, reply_markup=kb_age())


@dp.callback_query(F.data == "confirm_18")
async def confirm_18(callback: types.CallbackQuery):
    text = (
        "🖤 <b>ТЁМНАЯ СТОРОНА НЕ ДЛЯ ВСЕХ</b> 🖤\n\n"
        "Продолжая, ты подтверждаешь, что тебе уже есть 18 лет\n"
        "и ты находишься в здравом уме и памяти.\n\n"
        "Ты обязуешься соблюдать Правила DARK DESIRES PLAY:\n\n"
        "1. Всё, что происходит здесь — остаётся здесь.\n"
        "2. Анонимность — священна. Не нарушай её.\n"
        "3. Уважай других. Без осуждения. Без давления.\n"
        "4. Всё — только по взаимному согласию.\n"
        "5. Нарушил — вылетел. Без обсуждений.\n\n"
        "Продолжая, ты принимаешь правила и условия клуба."
    )
    await callback.message.edit_text(text, reply_markup=kb_rules())


@dp.callback_query(F.data == "accept_rules")
async def accept_rules(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("→ Отлично. Давай узнаем друг друга получше...")
    await asyncio.sleep(1.5)
    await callback.message.edit_text("Кто ты?", reply_markup=kb_gender())
    await state.set_state(Register.gender)


@dp.callback_query(Register.gender, F.data.startswith("gender_"))
async def reg_gender(callback: types.CallbackQuery, state: FSMContext):
    genders = {"gender_m": "Мужчина", "gender_f": "Женщина", "gender_o": "Другое"}
    gender = genders[callback.data]
    await state.update_data(gender=gender)
    await callback.message.edit_text("Кто тебе интересен?", reply_markup=kb_search_for())
    await state.set_state(Register.search_for)


@dp.callback_query(Register.search_for, F.data.startswith("search_"))
async def reg_search(callback: types.CallbackQuery, state: FSMContext):
    search_map = {"search_m": "Мужчин", "search_f": "Женщин", "search_a": "Всех"}
    search_for = search_map[callback.data]
    await state.update_data(search_for=search_for)
    await callback.message.edit_text("Где тебя искать? 🏙\n\nВведи свой город сообщением.")
    await state.set_state(Register.city)


@dp.message(Register.city)
async def reg_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer(
        "Расскажи пару слов о себе.\n(или напиши /skip, если хочешь остаться загадкой)"
    )
    await state.set_state(Register.about)


@dp.message(Register.about)
async def reg_about(message: types.Message, state: FSMContext):
    await state.update_data(about=message.text)
    data = await state.get_data()
    user_profiles[message.from_user.id] = data
    await state.clear()

    profile = (
        f"💋 <b>Твоя анкета готова!</b>\n\n"
        f"Пол: {data['gender']}\n"
        f"Ищешь: {data['search_for']}\n"
        f"Город: {data['city']}\n"
        f"О себе: {data['about']}\n\n"
        f"🔥 Теперь ты часть DARK DESIRES PLAY."
    )
    await message.answer(profile)


@dp.message(Register.about, F.text == "/skip")
async def reg_skip(message: types.Message, state: FSMContext):
    await state.update_data(about="—")
    data = await state.get_data()
    user_profiles[message.from_user.id] = data
    await state.clear()

    profile = (
        f"💋 <b>Твоя анкета готова!</b>\n\n"
        f"Пол: {data['gender']}\n"
        f"Ищешь: {data['search_for']}\n"
        f"Город: {data['city']}\n\n"
        f"🔥 Теперь ты часть DARK DESIRES PLAY."
    )
    await message.answer(profile)


# ======================
# Run
# ======================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
