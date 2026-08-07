from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from yookassa import Payment
import uuid
from app.payment.crud import (
    update_premium,
    deactivate_all_referrers,
    has_active_referrer,
    get_active_referrer,
)
from app.payment.keyboard import payment_keyboard
from app.payment.state import PaymentState
from app.start.crud import create_user
from core.models import db_helper

router = Router()

# Цены
PRICE_WITHOUT_REFERRER = 500.00
PRICE_WITH_REFERRER = 350.00


@router.message(F.text == "💎 Premium подписка")
async def create_payment(message: Message, state: FSMContext):
    try:
        async with db_helper.scoped_session_dependency() as session:
            user = await create_user(
                session, message.from_user.id, message.from_user.username
            )

            # Проверяем наличие активного реферера
            has_referrer = await has_active_referrer(session, message.from_user.id)
            print(has_referrer)
            # Определяем цену
            final_price = (
                PRICE_WITH_REFERRER if has_referrer else PRICE_WITHOUT_REFERRER
            )

            # Отправляем сообщение с информацией о цене
            if has_referrer:
                referrer = await get_active_referrer(session, message.from_user.id)
                referrer_name = (
                    referrer.username or str(referrer.telegram_id)
                    if referrer
                    else "реферер"
                )

                await message.answer(
                    f"🎉 У вас есть активный реферер (@{referrer_name})!\n"
                    f"Вы получаете скидку 10% на Premium подписку!\n"
                    f"💰 Цена: {final_price} ₽ (вместо {PRICE_WITHOUT_REFERRER} ₽)"
                )
            else:
                await message.answer(
                    f"💎 Стоимость Premium подписки: {final_price} ₽\n"
                    "👥 Пригласите друга и получите скидку 30%!\n"
                    "Просто отправьте ему вашу реферальную ссылку."
                )

        order_id = str(uuid.uuid4())

        payment = Payment.create(
            {
                "amount": {"value": final_price, "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://t.me/ваш_бот",
                },
                "capture": True,
                "description": f"Premium подписка. Заказ #{order_id[:8]}",
                "metadata": {
                    "user_id": str(message.from_user.id),
                    "order_id": order_id,
                    "has_referrer": str(has_referrer),
                    "price": str(final_price),
                },
            }
        )

        confirmation_url = payment.confirmation.confirmation_url

        await state.set_state(PaymentState.payment_id)
        await state.update_data(
            payment_id=payment.id, has_referrer=has_referrer, price=final_price
        )

        return await message.answer(
            """💎 Для оплаты подписки перейдите по ссылке:\nПосле оплаты нажмите кнопку 'Проверить'""",
            reply_markup=payment_keyboard(confirmation_url),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании платежа: {str(e)}")


@router.callback_query(F.data == "payment_check")
async def payment_check(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state != PaymentState.payment_id:
        await callback.message.answer("❌ Нет активного платежа")
        return

    data = await state.get_data()
    payment_id = data.get("payment_id")
    has_referrer = data.get("has_referrer", False)

    try:
        payment = Payment.find_one(payment_id)

        if payment.status == "succeeded":
            async with db_helper.scoped_session_dependency() as session:
                # Активируем премиум
                user = await update_premium(session, callback.from_user.id)

                if user:
                    # Если использовали скидку по рефереру
                    if has_referrer:
                        # Деактивируем ВСЕХ рефереров (если их несколько)
                        deactivated_count = await deactivate_all_referrers(
                            session, callback.from_user.id
                        )

                        await callback.message.answer(
                            f"✅ Платеж оплачен! Подписка активирована!\n"
                            f"🎉 Использована реферальная скидка. "
                            f"Деактивировано рефереров: {deactivated_count}"
                        )
                    else:
                        await callback.message.answer(
                            "✅ Платеж оплачен! Подписка активирована!\n"
                            "👥 Пригласите друзей и получайте скидки в будущем!"
                        )
                else:
                    await callback.message.answer("❌ Пользователь не найден")

                await state.clear()

        elif payment.status == "pending" or payment.status == "waiting_for_capture":
            await callback.message.answer("⏳ Платеж еще не оплачен")
        elif payment.status == "canceled":
            await callback.message.answer("❌ Платеж отменен")
            await state.clear()
        else:
            await callback.message.answer(f"ℹ️ Статус: {payment.status}")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")
