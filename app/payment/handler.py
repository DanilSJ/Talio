from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from yookassa import Payment
import uuid

from app.payment.crud import update_premium, del_referrer
from app.payment.keyboard import payment_keyboard
from app.payment.state import PaymentState
from app.start.crud import create_user
from core.models import db_helper

router = Router()


@router.message(F.text == "💎 Premium подписка")
async def create_payment(message: Message, state: FSMContext):
    try:
        price = 500.00
        async with db_helper.scoped_session_dependency() as session:
            user = await create_user(
                session, message.from_user.id, message.from_user.username
            )

            if user.referrer_is_active:
                price = 350.00

        order_id = str(uuid.uuid4())

        payment = Payment.create(
            {
                "amount": {"value": price, "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://t.me/ваш_бот",
                },
                "capture": True,
                "description": f"Premium подписка. Заказ #{order_id[:8]}",
                "metadata": {
                    "user_id": str(message.from_user.id),
                    "order_id": order_id,
                },
            }
        )

        confirmation_url = payment.confirmation.confirmation_url

        await state.set_state(PaymentState.payment_id)
        await state.update_data(payment_id=payment.id)

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
    try:
        payment = Payment.find_one(payment_id)

        if payment.status == "succeeded":
            async with db_helper.scoped_session_dependency() as session:
                await update_premium(session, callback.from_user.id)
                await del_referrer(session, callback.message.from_user.id)
                await callback.message.answer(
                    "✅ Платеж оплачен! Подписка активирована!"
                )
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
