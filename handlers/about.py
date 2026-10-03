"""О нас / Контакты."""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import back_menu
from content import ABOUT_TEXT

router = Router()


@router.callback_query(F.data == "menu_about")
async def cb_menu_about(call: CallbackQuery):
    await call.message.edit_text(ABOUT_TEXT, reply_markup=back_menu())
    await call.answer()
