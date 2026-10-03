"""Выкупить у меня — FSM-заявка."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import cancel_fsm, back_menu
from database import add_order
from config import ADMIN_ID
from utils import DEVICES_RU, CONDITIONS_RU

router = Router()


class SellForm(StatesGroup):
    device = State()
    model = State()
    condition = State()
    price = State()
    contact = State()


@router.callback_query(F.data == "menu_sell")
async def cb_menu_sell(call: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 iPhone", callback_data="sell_dev_iphone"),
         InlineKeyboardButton(text="📲 iPad", callback_data="sell_dev_ipad")],
        [InlineKeyboardButton(text="💻 MacBook", callback_data="sell_dev_macbook"),
         InlineKeyboardButton(text="🎮 PlayStation", callback_data="sell_dev_ps")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="fsm_cancel")],
    ])
    await call.message.edit_text(
        "💰 <b>Выкуп техники</b>\n\n"
        "Заполни короткую заявку — мы свяжемся и подтвердим цену.\n\n"
        "<b>Шаг 1/5.</b> Выбери устройство:",
        reply_markup=kb,
    )
    await state.set_state(SellForm.device)
    await call.answer()


@router.callback_query(SellForm.device, F.data.startswith("sell_dev_"))
async def sell_device(call: CallbackQuery, state: FSMContext):
    device = call.data.replace("sell_dev_", "")
    await state.update_data(device=device)
    await call.message.edit_text(
        f"✅ Устройство: <b>{DEVICES_RU.get(device, device)}</b>\n\n"
        f"<b>Шаг 2/5.</b> Напиши модель (например: <i>iPhone 15 Pro</i>):",
        reply_markup=cancel_fsm(),
    )
    await state.set_state(SellForm.model)
    await call.answer()


@router.message(SellForm.model)
async def sell_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text.strip())
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Идеальное", callback_data="sell_cond_ideal")],
        [InlineKeyboardButton(text="Хорошее", callback_data="sell_cond_good")],
        [InlineKeyboardButton(text="Заметные следы", callback_data="sell_cond_worn")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="fsm_cancel")],
    ])
    await message.answer(
        f"✅ Модель: <b>{message.text}</b>\n\n"
        f"<b>Шаг 3/5.</b> Выбери состояние:",
        reply_markup=kb,
    )
    await state.set_state(SellForm.condition)


@router.callback_query(SellForm.condition, F.data.startswith("sell_cond_"))
async def sell_condition(call: CallbackQuery, state: FSMContext):
    cond = call.data.replace("sell_cond_", "")
    await state.update_data(condition=cond)
    await call.message.edit_text(
        f"✅ Состояние: <b>{CONDITIONS_RU.get(cond, cond)}</b>\n\n"
        f"<b>Шаг 4/5.</b> Напиши желаемую цену в рублях (только цифры):",
        reply_markup=cancel_fsm(),
    )
    await state.set_state(SellForm.price)
    await call.answer()


@router.message(SellForm.price)
async def sell_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.replace(" ", "").replace("₽", ""))
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введи число. Например: <i>50000</i>")
        return
    await state.update_data(price=price)
    await message.answer(
        f"✅ Цена: <b>{price:,} ₽</b>\n\n".replace(",", " ") +
        f"<b>Шаг 5/5.</b> Как с тобой связаться? Напиши @username или телефон:",
        reply_markup=cancel_fsm(),
    )
    await state.set_state(SellForm.contact)


@router.message(SellForm.contact)
async def sell_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    contact = message.text.strip()
    user = message.from_user

    order_id = add_order(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name,
        device=DEVICES_RU.get(data["device"], data["device"]),
        model=data["model"],
        condition=CONDITIONS_RU.get(data["condition"], data["condition"]),
        price=data["price"],
        contact=contact,
    )

    admin_text = (
        f"🔔 <b>Новая заявка №{order_id}</b>\n\n"
        f"👤 {user.full_name}"
        + (f" (@{user.username})" if user.username else "")
        + f"\n🆔 <code>{user.id}</code>\n\n"
        f"📱 {data['device']} <b>{data['model']}</b>\n"
        f"⚙️ {CONDITIONS_RU.get(data['condition'], data['condition'])}\n"
        f"💵 {data['price']:,} ₽\n".replace(",", " ") +
        f"📞 {contact}"
    )
    try:
        await message.bot.send_message(ADMIN_ID, admin_text)
    except Exception as e:
        import logging
        logging.getLogger("itradebot").error(f"Не отправил заявку админу: {e}")

    await state.clear()
    await message.answer(
        f"✅ <b>Заявка №{order_id} отправлена!</b>\n\n"
        f"Мы свяжемся с тобой по контакту <b>{contact}</b> в ближайшее время.\n\n"
        f"Посмотреть статус можно в разделе «📋 Мои заявки».",
        reply_markup=back_menu(),
    )


@router.callback_query(F.data.startswith("submit_"))
async def cb_submit(call: CallbackQuery):
    payload = call.data.replace("submit_", "", 1)
    from utils import parse_payload
    info = parse_payload(payload)
    user = call.from_user

    admin_text = (
        f"🔔 <b>Заявка с сайта</b>\n\n"
        f"👤 {user.full_name}"
        + (f" (@{user.username})" if user.username else "")
        + f"\n🆔 <code>{user.id}</code>\n\n"
        f"📱 {info.get('device', '—')} <b>{info.get('model', '—')}</b>\n"
        f"⚙️ {info.get('condition', '—')}"
    )
    try:
        await call.bot.send_message(ADMIN_ID, admin_text)
        await call.message.edit_text(
            "✅ <b>Заявка отправлена!</b>\n\nМы свяжемся с тобой в ближайшее время.",
            reply_markup=back_menu(),
        )
    except Exception:
        await call.message.edit_text(
            "⚠️ Не удалось отправить заявку. Напиши нам в поддержку.",
            reply_markup=back_menu(),
        )
    await call.answer("Заявка отправлена")
