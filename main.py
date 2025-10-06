import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request
import uvicorn

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ======================
# ENV & Bot
# ======================
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # пример: https://dark-desires-play-bot.onrender.com/webhook

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ======================
# FastAPI app
# ======================
app = FastAPI()


# --- Health-check (убирает 404 на корне и удобен для пингера) ---
@app.get("/")
async def health():
    return {"status": "ok", "app": "Dark Desires Play"}


# --- Webhook endpoint (ВАЖНО: парсим Update корректно) ---
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()                      # dict из Telegram
    update = types.Update.model_validate(data)       # превращаем в aiogram.types.Update
    await dp.feed_update(bot, update)                # скармливаем диспетчеру
    return {"status": "ok"}


# --- Ставит вебхук автоматически при старте приложения ---
@app.on_event("startup")
async def on_startup():
    if WEBHOOK_URL:
        try:
            await bot.set_webhook(WEBHOOK_URL)
        except Exception as e:
            # Не падаем из-за вебхука — просто логируем
            print(f"Can't set webhook: {e}")


# ======================
# UI helpers
# ======================
def kb_enter() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖤 ВОЙТИ НА ТЁМНУЮ СТОРОНУ 🖤", callback_data="enter_dark_side")]
        ]
    )

def kb_age() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Мне 18", callback_data="confirm_age")]
        ]
    )


# ======================
# Handlers
# ======================
@dp.message(CommandStart())
async def start(message: types.Message):
    # Чистим /start, чтобы экран выглядел опрятно
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass

    text = (
        "🕶 <b>Добро пожаловать в DARK DESIRES PLAY</b> 🔥\n\n"
        "Здесь нет имён. Только желания.\n"
        "Анонимность. Игра. Страсть.\n\n"
        "<i>Нажми, чтобы сделать первый шаг…</i>"
    )
    await message.answer(text, reply_markup=kb_enter())


@dp.callback_query(F.data == "enter_dark_side")
async def enter_dark_side(callback: types.CallbackQuery):
    text = (
        "🌒 <b>Добро пожаловать на тёмную сторону.</b>\n\n"
        "Подтверди, что тебе 18 лет, чтобы продолжить."
    )
    await callback.message.edit_text(text, reply_markup=kb_age())


@dp.callback_query(F.data == "confirm_age")
async def confirm_age(callback: types.CallbackQuery):
    text = (
        "💋 Отлично.\n"
        "Теперь ты внутри игры желаний.\n\n"
        "<i>Меню скоро будет доступно...</i>"
    )
    await callback.message.edit_text(text)


# ======================
# Run (локально / на Render)
# ======================
if __name__ == "__main__":
    print("🤖 Dark Desires Play Bot запущен...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
