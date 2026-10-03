"""Купить — категории и список товаров."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import buy_categories
from content import CATALOG
from utils import DEVICES_RU

router = Router()


@router.callback_query(F.data == "menu_buy")
async def cb_menu_buy(call: CallbackQuery):
    await call.message.edit_text(
        "🛒 <b>Купить технику</b>\n\n"
        "Выбери категорию — покажу актуальные позиции с ценами.",
        reply_markup=buy_categories(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("cat_"))
async def cb_category(call: CallbackQuery):
    cat = call.data.replace("cat_", "")
    items = CATALOG.get(cat, [])

    if not items:
        await call.answer("Пока пусто в этой категории", show_alert=True)
        return

    lines = []
    for item in items:
        price_str = f"{item['price']:,}".replace(",", " ")
        lines.append(f"• <b>{item['name']}</b>\n  {item['meta']}\n  💵 {price_str} ₽")

    text = f"📦 <b>{DEVICES_RU.get(cat, cat.capitalize())}</b>\n\n" + "\n\n".join(lines)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Заказать", callback_data="menu_support")],
        [InlineKeyboardButton(text="◀️ К категориям", callback_data="menu_buy")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu_back")],
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()
