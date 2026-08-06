from aiogram import Router, F
from aiogram.types import Message
from app.start.crud import create_user
from core.models import db_helper

router = Router()


@router.message(F.text == "👤 Личный кабинет")
async def account(message: Message):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, message.from_user.id, message.from_user.username
        )

        return await message.answer(
            f"""Твой ID: {user.telegram_id}
Регистрация: {user.create_at}
Премиум: {user.premium}
Приглашено друзей: {user.referral_users} чел
Реферальная ссылка (10% скидна на premium): https://t.me/bot?start={user.telegram_id}"""
        )
