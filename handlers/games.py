"""Игры PS5 — новинки и хиты."""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import games_menu
from content import GAMES_NEW, GAMES_HITS

router = Router()


def _fmt(items):
    lines = []
    for g in items:
        price_str = f"{g['price']:,}".replace(",", " ")
        lines.append(f"• <b>{g['name']}</b>\n  {g['meta']}\n  💵 {price_str} ₽")
    return "\n\n".join(lines)


@router.callback_query(F.data == "menu_games")
async def cb_menu_games(call: CallbackQuery):
    await call.message.edit_text(
        "🎮 <b>Игры PS5</b>\n\n"
        "Диски и цифровые версии. Все игры проверены, работают на российских аккаунтах.",
        reply_markup=games_menu(),
    )
    await call.answer()


@router.callback_query(F.data == "games_new")
async def cb_games_new(call: CallbackQuery):
    await call.message.edit_text("🔥 <b>Новинки</b>\n\n" + _fmt(GAMES_NEW), reply_markup=games_menu())
    await call.answer()


@router.callback_query(F.data == "games_hits")
async def cb_games_hits(call: CallbackQuery):
    await call.message.edit_text("🏆 <b>Хиты</b>\n\n" + _fmt(GAMES_HITS), reply_markup=games_menu())
    await call.answer()
