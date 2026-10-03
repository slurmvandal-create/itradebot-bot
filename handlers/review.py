"""Отзыв: текст → фото → оценка → сохранение → админу."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import rating_kb, skip_photo, back_menu, review_publish_kb
from database import add_review
from config import ADMIN_ID

router = Router()


class ReviewForm(StatesGroup):
    text = State()
    photo = State()
    rating = State()


@router.callback_query(F.data == "menu_review")
async def cb_menu_review(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "✍️ <b>Оставить отзыв</b>\n\n"
        "Напиши пару слов о работе с iTradeBot — что понравилось, что улучшить.\n\n"
        "<i>Шаг 1/3.</i> Отправь текст отзыва:",
        reply_markup=back_menu(),
    )
    await state.set_state(ReviewForm.text)
    await call.answer()


@router.message(ReviewForm.text)
async def review_text(message: Message, state: FSMContext):
    if len(message.text or "") < 3:
        await message.answer("⚠️ Слишком коротко. Напиши хотя бы пару слов:")
        return
    await state.update_data(text=message.text.strip())
    await message.answer(
        "✅ Текст принят.\n\n<i>Шаг 2/3.</i> Прикрепи фото (или пропусти):",
        reply_markup=skip_photo(),
    )
    await state.set_state(ReviewForm.photo)


@router.message(ReviewForm.photo, F.photo)
async def review_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await message.answer(
        "✅ Фото принято.\n\n<i>Шаг 3/3.</i> Поставь оценку:",
        reply_markup=rating_kb(),
    )
    await state.set_state(ReviewForm.rating)


@router.message(ReviewForm.photo)
async def review_photo_invalid(message: Message):
    await message.answer("⚠️ Отправь фото или нажми «Пропустить».")


@router.callback_query(ReviewForm.photo, F.data == "review_skip_photo")
async def review_skip_photo(call: CallbackQuery, state: FSMContext):
    await state.update_data(photo_id=None)
    await call.message.edit_text(
        "✅ Фото пропущено.\n\n<i>Шаг 3/3.</i> Поставь оценку:",
        reply_markup=rating_kb(),
    )
    await state.set_state(ReviewForm.rating)
    await call.answer()


@router.callback_query(ReviewForm.rating, F.data.startswith("rate_"))
async def review_rating(call: CallbackQuery, state: FSMContext):
    rating = int(call.data.replace("rate_", ""))
    data = await state.get_data()
    user = call.from_user

    review_id = add_review(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name,
        text=data["text"],
        photo_id=data.get("photo_id"),
        rating=rating,
    )

    stars = "⭐" * rating
    admin_text = (
        f"📝 <b>Новый отзыв №{review_id}</b>\n\n"
        f"👤 {user.full_name}"
        + (f" (@{user.username})" if user.username else "")
        + f"\n🆔 <code>{user.id}</code>\n\n"
        f"Оценка: {stars} ({rating}/5)\n\n"
        f"<i>{data['text']}</i>"
    )

    try:
        if data.get("photo_id"):
            await call.bot.send_photo(
                ADMIN_ID,
                photo=data["photo_id"],
                caption=admin_text,
                reply_markup=review_publish_kb(review_id),
            )
        else:
            await call.bot.send_message(
                ADMIN_ID,
                admin_text,
                reply_markup=review_publish_kb(review_id),
            )
    except Exception as e:
        import logging
        logging.getLogger("itradebot").error(f"Не отправил отзыв админу: {e}")

    await state.clear()
    await call.message.edit_text(
        f"🙏 <b>Спасибо за отзыв!</b>\n\nТвоя оценка: {stars}\n\nМы обязательно учтём твоё мнение.",
        reply_markup=back_menu(),
    )
    await call.answer("Отзыв сохранён")
