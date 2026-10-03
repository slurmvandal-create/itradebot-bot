"""Поддержка."""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import support_kb
from config import SUPPORT_USERNAME

router = Router()


@router.callback_query(F.data == "menu_support")
async def cb_menu_support(call: CallbackQuery):
    await call.message.edit_text(
        "🆘 <b>Поддержка</b>\n\n"
        f"Напиши нам напрямую: @{SUPPORT_USERNAME}\n\n"
        "Отвечаем обычно в течение 15 минут в рабочее время (10:00–20:00).",
        reply_markup=support_kb(),
    )
    await call.answer()
