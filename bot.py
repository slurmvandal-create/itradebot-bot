"""
iTradeBot — Telegram-бот для iTradeBot лендинга
Стек: Python 3.11+ / aiogram 3.x
"""

import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# ---------- Конфигурация ----------
load_dotenv(Path(__file__).parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
SITE_URL = os.getenv("SITE_URL", "https://itradebot.netlify.app")

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN не найден в .env")
if not ADMIN_ID:
    raise SystemExit("❌ ADMIN_ID не найден в .env")

# ---------- Логирование ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("itradebot")

# ---------- Инициализация ----------
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# ---------- Клавиатуры ----------
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛒 Продать технику", callback_data="menu_sell"),
            InlineKeyboardButton(text="📱 Купить технику", callback_data="menu_buy"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="menu_help"),
        ],
    ])


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
    ])


def site_button(path: str, text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, url=f"{SITE_URL}{path}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
    ])


# ---------- Хелпер: разбор payload ----------
def parse_payload(payload: str) -> dict:
    """
    Примеры payload с сайта:
      sell
      sell_iphone_iPhone-15-Pro_ideal
      buy_1
      buy_4
      header
      catalog
      cta
      cta_sell
    """
    if not payload:
        return {"type": "empty", "raw": ""}

    parts = payload.split("_", 3)
    kind = parts[0]

    if kind == "sell":
        result = {"type": "sell"}
        if len(parts) >= 2:
            result["device"] = parts[1]
        if len(parts) >= 3:
            result["model"] = parts[2].replace("-", " ")
        if len(parts) >= 4:
            result["condition"] = parts[3]
        return result

    if kind == "buy" and len(parts) >= 2:
        return {"type": "buy", "item_id": parts[1]}

    return {"type": kind, "raw": payload}


# ---------- Обработчики ----------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    payload = message.text.split(maxsplit=1)[1] if " " in message.text else ""
    info = parse_payload(payload)

    log.info(f"START from {message.from_user.id} | payload={payload!r} | parsed={info}")

    # Пользователь пришёл с сайта с готовой заявкой на выкуп
    if info["type"] == "sell" and info.get("model"):
        text = (
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Вижу, ты пришёл с оценкой:\n"
            f"<b>{info.get('model', '—')}</b>\n"
            f"Состояние: <b>{info.get('condition', '—')}</b>\n\n"
            f"Отправь заявку — мы подтвердим цену и свяжемся."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📨 Отправить заявку", callback_data=f"submit_{payload}")],
            [InlineKeyboardButton(text="🛒 Открыть каталог", url=f"{SITE_URL}#catalog")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu_back")],
        ])
        await message.answer(text, reply_markup=kb)
        return

    # Пользователь пришёл с конкретного товара
    if info["type"] == "buy":
        text = (
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Ты смотришь товар <b>#{info.get('item_id')}</b> на сайте.\n"
            f"Хочешь узнать подробности и оформить покупку?"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Открыть карточку", url=f"{SITE_URL}#catalog")],
            [InlineKeyboardButton(text="💬 Связаться", callback_data="menu_help")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu_back")],
        ])
        await message.answer(text, reply_markup=kb)
        return

    # Обычный старт
    text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        f"Это <b>iTradeBot</b> — выкуп и продажа техники в Екатеринбурге.\n\n"
        f"Выбери, что хочешь сделать:"
    )
    await message.answer(text, reply_markup=main_menu())


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>Помощь</b>\n\n"
        "• /start — главное меню\n"
        "• /help — эта справка\n\n"
        f"🌐 Сайт: {SITE_URL}\n"
        "📍 Екатеринбург и область\n"
        "🚚 Доставка по России (СДЭК, Почта)",
        reply_markup=back_menu(),
    )


# ---------- Callback'и меню ----------
@dp.callback_query(F.data == "menu_back")
async def cb_menu_back(call: CallbackQuery):
    await call.message.edit_text(
        f"👋 Привет, <b>{call.from_user.first_name}</b>!\n\n"
        f"Это <b>iTradeBot</b> — выкуп и продажа техники.\n\n"
        f"Выбери действие:",
        reply_markup=main_menu(),
    )
    await call.answer()


@dp.callback_query(F.data == "menu_sell")
async def cb_menu_sell(call: CallbackQuery):
    await call.message.edit_text(
        "🛒 <b>Продать технику</b>\n\n"
        "Пройди короткую оценку на сайте — это займёт 2 минуты.\n"
        "Предварительную цену увидишь сразу, финальную — после осмотра.",
        reply_markup=site_button("#estimate", "💻 Открыть оценку на сайте"),
    )
    await call.answer()


@dp.callback_query(F.data == "menu_buy")
async def cb_menu_buy(call: CallbackQuery):
    await call.message.edit_text(
        "📱 <b>Купить технику</b>\n\n"
        "В каталоге — iPhone, iPad, MacBook, PlayStation и игры.\n"
        "Вся техника проверена, есть гарантия магазина.",
        reply_markup=site_button("#catalog", "🛍 Открыть каталог"),
    )
    await call.answer()


@dp.callback_query(F.data == "menu_help")
async def cb_menu_help(call: CallbackQuery):
    await call.message.edit_text(
        "ℹ️ <b>Помощь</b>\n\n"
        "По вопросам выкупа, покупки и доставки — напиши нам:\n"
        f"🌐 Сайт: {SITE_URL}\n"
        "📍 Екатеринбург и область\n"
        "🚚 Доставка по России (СДЭК, Почта)",
        reply_markup=back_menu(),
    )
    await call.answer()


# ---------- Отправка заявки админу ----------
@dp.callback_query(F.data.startswith("submit_"))
async def cb_submit(call: CallbackQuery):
    payload = call.data.replace("submit_", "", 1)
    info = parse_payload(payload)
    user = call.from_user

    admin_text = (
        f"🔔 <b>Новая заявка на выкуп</b>\n\n"
        f"👤 {user.full_name}"
        + (f" (@{user.username})" if user.username else "")
        + f"\n🆔 <code>{user.id}</code>\n\n"
        f"📱 Устройство: <b>{info.get('model', '—')}</b>\n"
        f"⚙️ Состояние: <b>{info.get('condition', '—')}</b>\n"
        f"📦 Тип: <b>{info.get('device', '—')}</b>"
    )

    try:
        await bot.send_message(ADMIN_ID, admin_text)
        await call.message.edit_text(
            "✅ <b>Заявка отправлена!</b>\n\n"
            "Мы свяжемся с тобой в ближайшее время для подтверждения цены.",
            reply_markup=back_menu(),
        )
    except Exception as e:
        log.error(f"Не удалось отправить заявку админу: {e}")
        await call.message.edit_text(
            "⚠️ Не удалось отправить заявку. Попробуй позже или напиши нам напрямую.",
            reply_markup=back_menu(),
        )
    await call.answer("Заявка отправлена")


# ---------- Fallback ----------
@dp.message()
async def fallback(message: Message):
    await message.answer(
        "Я пока понимаю только команды. Открой меню:",
        reply_markup=main_menu(),
    )


# ---------- Точка входа ----------
async def main():
    log.info("🚀 Запускаю iTradeBot...")
    log.info(f"ADMIN_ID = {ADMIN_ID}")
    log.info(f"SITE_URL = {SITE_URL}")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Бот остановлен")
