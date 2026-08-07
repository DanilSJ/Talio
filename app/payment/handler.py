from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from yookassa import Payment
import uuid
from app.payment.crud import (
    update_premium,
    deactivate_all_referrers,
    has_active_referrer,
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
async def show_tariffs(message: Message, state: FSMContext):
    """Показывает тарифы с выбором периода"""
    try:
        async with db_helper.scoped_session_dependency() as session:
            user = await create_user(
                session, message.from_user.id, message.from_user.username
            )

            # Проверяем наличие активного реферера
            has_referrer = await has_active_referrer(session, message.from_user.id)

            # Рассчитываем цены для каждого тарифа
            if has_referrer:
                one_month = round(PRICE_WITH_REFERRER, 2)
                three_month = round(
                    PRICE_WITH_REFERRER * 3 * 0.9, 2
                )  # 10% скидка за 3 месяца
                six_month = round(
                    PRICE_WITH_REFERRER * 6 * 0.8, 2
                )  # 20% скидка за 6 месяцев
                discount_text = "🎉 Скидка по реферальной ссылке 10%!\n"
            else:
                one_month = round(PRICE_WITHOUT_REFERRER, 2)
                three_month = round(PRICE_WITHOUT_REFERRER * 3 * 0.9, 2)
                six_month = round(PRICE_WITHOUT_REFERRER * 6 * 0.8, 2)
                discount_text = ""

            # Создаем клавиатуру с выбором тарифа
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"1 месяц - {one_month} ₽",
                            callback_data=f"tariff_1month_{one_month}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=f"3 месяца - {three_month} ₽ (скидка 10%)",
                            callback_data=f"tariff_3months_{three_month}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=f"6 месяцев - {six_month} ₽ (скидка 20%)",
                            callback_data=f"tariff_6months_{six_month}",
                        )
                    ],
                ]
            )

            text = (
                f"💎 Выберите период Premium подписки:\n\n"
                f"📅 1 месяц - {one_month} ₽\n"
                f"📅 3 месяца - {three_month} ₽ (экономия 10%)\n"
                f"📅 6 месяцев - {six_month} ₽ (экономия 20%)\n\n"
                f"{discount_text}"
                f"👥 Пригласите друга и получите скидку 10%!\n"
                f"Просто отправьте ему вашу реферальную ссылку."
            )

            await message.answer(text, reply_markup=keyboard)

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(F.data.startswith("tariff_"))
async def create_payment(callback: CallbackQuery, state: FSMContext):
    """Создает платеж для выбранного тарифа"""
    try:
        # Извлекаем данные из callback_data
        _, tariff, price = callback.data.split("_")

        # Определяем период подписки
        if tariff == "1month":
            period = 1
            period_text = "1 месяц"
        elif tariff == "3months":
            period = 3
            period_text = "3 месяца"
        elif tariff == "6months":
            period = 6
            period_text = "6 месяцев"
        else:
            await callback.answer("❌ Неизвестный тариф")
            return

        price = float(price)

        async with db_helper.scoped_session_dependency() as session:
            has_referrer = await has_active_referrer(session, callback.from_user.id)

        # Создаем платеж
        order_id = str(uuid.uuid4())

        payment = Payment.create(
            {
                "amount": {"value": str(price), "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://t.me/ваш_бот",
                },
                "capture": True,
                "description": f"Premium подписка на {period_text}. Заказ #{order_id[:8]}",
                "metadata": {
                    "user_id": str(callback.from_user.id),
                    "order_id": order_id,
                    "has_referrer": str(has_referrer),
                    "price": str(price),
                    "period": str(period),  # Сохраняем период подписки
                    "period_text": period_text,
                },
            }
        )

        # Сохраняем данные в состояние
        await state.set_state(PaymentState.payment_id)
        await state.update_data(
            payment_id=payment.id,
            has_referrer=has_referrer,
            price=price,
            period=period,
            period_text=period_text,
        )

        confirmation_url = payment.confirmation.confirmation_url

        await callback.message.delete()  # Удаляем сообщение с выбором тарифа
        await callback.message.answer(
            f"💎 Вы выбрали: {period_text}\n"
            f"💰 Сумма к оплате: {price} ₽\n\n"
            f"Для оплаты подписки перейдите по ссылке:\n"
            f"После оплаты нажмите кнопку 'Проверить'",
            reply_markup=payment_keyboard(confirmation_url),
        )

        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")
        await callback.message.answer(f"❌ Ошибка при создании платежа: {str(e)}")


@router.callback_query(F.data == "payment_check")
async def payment_check(callback: CallbackQuery, state: FSMContext):
    """Проверка статуса платежа"""
    current_state = await state.get_state()
    if current_state != PaymentState.payment_id:
        await callback.message.answer("❌ Нет активного платежа")
        return

    data = await state.get_data()
    payment_id = data.get("payment_id")
    has_referrer = data.get("has_referrer", False)
    period = data.get("period", 1)  # По умолчанию 1 месяц
    period_text = data.get("period_text", "1 месяц")

    try:
        payment = Payment.find_one(payment_id)

        if payment.status == "succeeded":
            async with db_helper.scoped_session_dependency() as session:
                user = await update_premium(session, callback.from_user.id, period)

                if user:
                    response_text = (
                        f"✅ Платеж оплачен!\n"
                        f"📅 Подписка активирована на {period_text}!\n"
                    )

                    # Если использовали скидку по рефереру
                    if has_referrer:
                        # Деактивируем ВСЕХ рефереров (если их несколько)
                        deactivated_count = await deactivate_all_referrers(
                            session, callback.from_user.id
                        )

                        response_text += (
                            f"🎉 Использована реферальная скидка.\n"
                            f"Деактивировано рефереров: {deactivated_count}"
                        )
                    else:
                        response_text += (
                            "👥 Пригласите друзей и получайте скидки в будущем!"
                        )

                    await callback.message.answer(response_text)
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
