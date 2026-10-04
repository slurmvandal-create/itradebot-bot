"""Мои заявки."""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import back_menu
from database import list_user_orders
from utils import STATUS_RU, fmt_date

router = Router()


@router.callback_query(F.data == "menu_orders")
async def cb_menu_orders(call: CallbackQuery):
    orders = list_user_orders(call.from_user.id)

    if not orders:
        await call.message.edit_text(
            "📋 <b>Мои заявки</b>\n\n"
            "У тебя пока нет заявок.\n\n"
            "Оформить первую можно через «💰 Выкупить у меня».",
            reply_markup=back_menu(),
        )
        await call.answer()
        return

    lines = []
    for o in orders[:10]:
        oid, device, model, condition, price, status, created = o
        price_str = f"{price:,}".replace(",", " ")
        lines.append(
            f"<b>№{oid}</b> · {device} {model}\n"
            f"⚙️ {condition} · 💵 {price_str} ₽\n"
            f"📅 {fmt_date(created)}\n"
            f"Статус: {STATUS_RU.get(status, status)}"
        )

    text = "📋 <b>Мои заявки</b>\n\n" + "\n\n".join(lines)
    await call.message.edit_text(text, reply_markup=back_menu())
    await call.answer()
