"""Все inline-клавиатуры."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SITE_URL, SUPPORT_USERNAME


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Выкупить у меня", callback_data="menu_sell"),
            InlineKeyboardButton(text="🛒 Купить", callback_data="menu_buy"),
        ],
        [
            InlineKeyboardButton(text="🎮 Игры PS5", callback_data="menu_games"),
            InlineKeyboardButton(text="📋 Мои заявки", callback_data="menu_orders"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ О нас / Контакты", callback_data="menu_about"),
            InlineKeyboardButton(text="🆘 Поддержка", callback_data="menu_support"),
        ],
        [
            InlineKeyboardButton(text="✍️ Оставить отзыв", callback_data="menu_review"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="menu_admin"),
        ],
    ])


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="menu_back")],
    ])


def site_button(path: str, text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, url=f"{SITE_URL}{path}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
    ])


def buy_categories() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 iPhone", callback_data="cat_iphone"),
         InlineKeyboardButton(text="📲 iPad", callback_data="cat_ipad")],
        [InlineKeyboardButton(text="💻 MacBook", callback_data="cat_macbook"),
         InlineKeyboardButton(text="🎮 PlayStation", callback_data="cat_ps")],
        [InlineKeyboardButton(text="🌐 Открыть каталог на сайте", url=f"{SITE_URL}#catalog")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
    ])


def games_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Новинки", callback_data="games_new")],
        [InlineKeyboardButton(text="🏆 Хиты", callback_data="games_hits")],
        [InlineKeyboardButton(text="🌐 Весь каталог игр на сайте", url=f"{SITE_URL}#catalog")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
    ])


def cancel_fsm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="fsm_cancel")],
    ])


def skip_photo() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Пропустить фото", callback_data="review_skip_photo")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="fsm_cancel")],
    ])


def rating_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐", callback_data="rate_1"),
            InlineKeyboardButton(text="⭐⭐", callback_data="rate_2"),
            InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3"),
            InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4"),
            InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5"),
        ],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="fsm_cancel")],
    ])


def support_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать в Telegram", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
    ])


def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Заявки", callback_data="admin_orders")],
        [InlineKeyboardButton(text="✍️ Отзывы", callback_data="admin_reviews")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
    ])


def order_status_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ В работе", callback_data=f"ostatus_{order_id}_in_progress"),
         InlineKeyboardButton(text="✔️ Завершена", callback_data=f"ostatus_{order_id}_done")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data=f"ostatus_{order_id}_cancelled")],
    ])


def review_publish_kb(review_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать на сайте", callback_data=f"rpublish_{review_id}")],
    ])