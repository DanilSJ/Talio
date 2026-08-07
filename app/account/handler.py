from aiogram import Router, F
from aiogram.types import Message

from app.account.crud import get_referrals_count
from app.start.crud import create_user
from core.config import settings
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
Приглашено друзей: {await get_referrals_count(session, message.from_user.id)} чел
Реферальная ссылка (10% скидна на premium): https://t.me/{settings.BOT_USERNAME}?start={user.telegram_id}"""
        )
