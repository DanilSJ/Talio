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
            f"""🆔 <b>Твой ID</b>: {user.telegram_id}
            
<b>🗓 Регистрация</b>: {user.create_at}
<b>💎 Премиум</b>: {user.premium}
<b>👥 Приглашено друзей</b>: {await get_referrals_count(session, message.from_user.id)} чел
<b>🌟 Реферальная ссылка (10% скидка на premium)</b>:
https://t.me/{settings.BOT_USERNAME}?start={user.telegram_id}""",
            parse_mode="HTML",
        )
