from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from yookassa import Payment
import uuid

from app.payment.crud import update_premium
from app.payment.keyboard import payment_keyboard
from app.payment.state import PaymentState
from core.models import db_helper

router = Router()


@router.message(F.text == "💎 Premium подписка")
async def create_payment(message: Message, state: FSMContext):
    try:
        order_id = str(uuid.uuid4())

        payment = Payment.create(
            {
                "amount": {"value": "500.00", "currency": "RUB"},
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

        await message.answer(
            """💎 Для оплаты подписки перейдите по ссылке:\nПосле оплаты нажмите кнопку 'Проверить'""",
            reply_markup=payment_keyboard(confirmation_url),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании платежа: {str(e)}")


@router.callback_query(F.data == "payment_check")
async def payment_check(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state != PaymentState.payment_id:
        await callback.answer("❌ Нет активного платежа")
        return

    data = await state.get_data()
    payment_id = data.get("payment_id")
    try:
        payment = Payment.find_one(payment_id)

        if payment.status == "succeeded":
            async with db_helper.scoped_session_dependency() as session:
                await update_premium(session, callback.message.from_user.id)
                await callback.answer("✅ Платеж оплачен! Подписка активирована!")
        elif payment.status == "pending" or payment.status == "waiting_for_capture":
            await callback.answer("⏳ Платеж еще не оплачен")
        elif payment.status == "canceled":
            await callback.answer("❌ Платеж отменен")
        else:
            await callback.answer(f"ℹ️ Статус: {payment.status}")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")
