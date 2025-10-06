import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import FastAPI, Request
import uvicorn
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# --- Приветственное сообщение ---
@dp.message(CommandStart())
async def start(message: types.Message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖤 ВОЙТИ НА ТЁМНУЮ СТОРОНУ 🖤", callback_data="enter_dark_side")]
        ]
    )

    await message.answer(
        text=(
            "🕶 <b>Добро пожаловать в DARK DESIRES PLAY</b> 🔥\n\n"
            "Здесь нет имён. Только желания.\n"
            "Анонимность. Игра. Страсть.\n\n"
            "<i>Нажми, чтобы сделать первый шаг…</i>"
        ),
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# --- Кнопка: Войти на тёмную сторону ---
@dp.callback_query(lambda c: c.data == "enter_dark_side")
async def enter_dark_side(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=(
            "🌒 <b>Добро пожаловать на тёмную сторону.</b>\n\n"
            "Подтверди, что тебе 18 лет, чтобы продолжить."
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="✅ Мне 18", callback_data="confirm_age")]]
        )
    )

# --- Подтверждение возраста ---
@dp.callback_query(lambda c: c.data == "confirm_age")
async def confirm_age(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=(
            "💋 Отлично.\n"
            "Теперь ты внутри игры желаний.\n\n"
            "<i>Меню скоро будет доступно...</i>"
        ),
        parse_mode="HTML"
    )

# --- Webhook route ---
@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    await dp.feed_update(bot, update)
    return {"status": "ok"}

if __name__ == "__main__":
    print("🤖 Dark Desires Play Bot запущен...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
