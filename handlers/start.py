"""Главное меню, /start, /help, Назад, отмена FSM."""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from keyboards import main_menu, back_menu
from utils import parse_payload
from config import SITE_URL

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    payload = message.text.split(maxsplit=1)[1] if " " in message.text else ""
    info = parse_payload(payload)

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
            [InlineKeyboardButton(text="🛒 Каталог", url=f"{SITE_URL}#catalog")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu_back")],
        ])
        await message.answer(text, reply_markup=kb)
        return

    if info["type"] == "buy":
        text = (
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Ты смотришь товар <b>#{info.get('item_id')}</b>.\n"
            f"Хочешь узнать подробности?"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍 Открыть карточку", url=f"{SITE_URL}#catalog")],
            [InlineKeyboardButton(text="💬 Связаться", callback_data="menu_support")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu_back")],
        ])
        await message.answer(text, reply_markup=kb)
        return

    text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        f"Это <b>iTradeBot</b> — выкуп и продажа техники в Екатеринбурге.\n\n"
        f"Выбери, что хочешь сделать:"
    )
    await message.answer(text, reply_markup=main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>Помощь</b>\n\n"
        "• /start — главное меню\n"
        "• /help — эта справка\n\n"
        f"🌐 Сайт: {SITE_URL}\n"
        "📍 Екатеринбург и область",
        reply_markup=back_menu(),
    )


@router.callback_query(F.data == "menu_back")
async def cb_menu_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        f"👋 Привет, <b>{call.from_user.first_name}</b>!\n\n"
        f"Это <b>iTradeBot</b> — выкуп и продажа техники.\n\n"
        f"Выбери действие:",
        reply_markup=main_menu(),
    )
    await call.answer()


@router.callback_query(F.data == "fsm_cancel")
async def cb_fsm_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ Действие отменено.\n\nВозвращаю в меню:",
        reply_markup=main_menu(),
    )
    await call.answer()
