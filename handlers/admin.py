"""Админ-панель: заявки, отзывы, рассылка."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from keyboards import admin_menu, back_menu, cancel_fsm
from database import (
    get_all_orders, update_order_status,
    get_all_reviews, publish_review, get_all_user_ids,
)
from utils import STATUS_RU, fmt_date

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.callback_query(F.data == "menu_admin")
async def cb_menu_admin(call: CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer("⛔ Доступ только для администратора", show_alert=True)
        return
    await call.message.edit_text("⚙️ <b>Админ-панель</b>\n\nВыбери раздел:", reply_markup=admin_menu())
    await call.answer()


@router.callback_query(F.data == "admin_orders")
async def cb_admin_orders(call: CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    orders = get_all_orders()

    if not orders:
        await call.message.edit_text("📋 <b>Заявки</b>\n\nПока пусто.", reply_markup=admin_menu())
        await call.answer()
        return

    lines = []
    for o in orders[:5]:
        oid, uid, uname, fname, device, model, cond, price, contact, status, created = o
        price_str = f"{price:,}".replace(",", " ")
        lines.append(
            f"<b>№{oid}</b> · {device} {model}\n"
            f"👤 {fname}" + (f" (@{uname})" if uname else "") + f" · 🆔 <code>{uid}</code>\n"
            f"⚙️ {cond} · 💵 {price_str} ₽\n"
            f"📞 {contact}\n"
            f"📅 {fmt_date(created)}\n"
            f"Статус: {STATUS_RU.get(status, status)}"
        )

    text = f"📋 <b>Заявки</b> (всего: {len(orders)})\n\n" + "\n\n———\n\n".join(lines)
    if len(orders) > 5:
        text += f"\n\n<i>...и ещё {len(orders) - 5}</i>"

    kb_rows = []
    for o in orders[:3]:
        oid = o[0]
        kb_rows.append([
            InlineKeyboardButton(text=f"✅ №{oid} в работу", callback_data=f"ostatus_{oid}_in_progress"),
            InlineKeyboardButton(text=f"✔️ №{oid} готово", callback_data=f"ostatus_{oid}_done"),
        ])
    kb_rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu_admin")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("ostatus_"))
async def cb_order_status(call: CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    parts = call.data.replace("ostatus_", "").rsplit("_", 1)
    if len(parts) != 2:
        await call.answer("Ошибка", show_alert=True)
        return
    oid, status = parts
    update_order_status(int(oid), status)
    await call.answer(f"Заявка №{oid}: {STATUS_RU.get(status, status)}", show_alert=True)


@router.callback_query(F.data == "admin_reviews")
async def cb_admin_reviews(call: CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    reviews = get_all_reviews()

    if not reviews:
        await call.message.edit_text("✍️ <b>Отзывы</b>\n\nПока пусто.", reply_markup=admin_menu())
        await call.answer()
        return

    lines = []
    for r in reviews[:5]:
        rid, uid, fname, text, photo, rating, published, created = r
        stars = "⭐" * rating
        pub = "✅" if published else "🕓"
        lines.append(
            f"<b>№{rid}</b> {pub} · {fname}\n"
            f"{stars} ({rating}/5) · 📅 {fmt_date(created)}\n"
            f"<i>{text[:200]}</i>"
        )

    text = f"✍️ <b>Отзывы</b> (всего: {len(reviews)})\n\n" + "\n\n———\n\n".join(lines)
    if len(reviews) > 5:
        text += f"\n\n<i>...и ещё {len(reviews) - 5}</i>"

    kb_rows = []
    for r in reviews[:3]:
        rid = r[0]
        if not r[6]:
            kb_rows.append([InlineKeyboardButton(text=f"✅ Опубликовать №{rid}", callback_data=f"rpublish_{rid}")])
    kb_rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu_admin")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("rpublish_"))
async def cb_publish_review(call: CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    rid = int(call.data.replace("rpublish_", ""))
    publish_review(rid)
    await call.answer(f"Отзыв №{rid} опубликован ✅", show_alert=True)


class BroadcastForm(StatesGroup):
    text = State()


@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(call: CallbackQuery, state: FSMContext):
    if not _is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    await call.message.edit_text(
        "📢 <b>Рассылка</b>\n\n"
        "Отправь текст, который получат все пользователи бота.\n\n"
        "<i>Можно с HTML-тегами: &lt;b&gt;, &lt;i&gt;, &lt;a&gt;</i>",
        reply_markup=cancel_fsm(),
    )
    await state.set_state(BroadcastForm.text)
    await call.answer()


@router.message(BroadcastForm.text)
async def broadcast_text(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    text = message.text
    user_ids = get_all_user_ids()

    sent, failed = 0, 0
    status_msg = await message.answer(f"📢 Начинаю рассылку на {len(user_ids)} чел....")

    for uid in user_ids:
        if uid == ADMIN_ID:
            continue
        try:
            await message.bot.send_message(uid, text)
            sent += 1
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"📢 <b>Рассылка завершена</b>\n\n✅ Доставлено: {sent}\n❌ Ошибок: {failed}",
        reply_markup=back_menu(),
    )
    await state.clear()
