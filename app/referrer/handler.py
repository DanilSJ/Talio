from aiogram import Router, F
from aiogram.types import Message

from app.account.crud import get_referrals_count
from app.referrer.keyboard import referrer_keyboard
from app.start.crud import create_user
from core.config import settings
from core.models import db_helper

router = Router()


@router.message(F.text == "👥 Пригласить друзей")
async def referrer(message: Message):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, message.from_user.id, message.from_user.username
        )
        url = f"https://t.me/{settings.BOT_USERNAME}?start={user.telegram_id}"
        return await message.answer(
            f"""<b>Пригласите друзей</b>
            
Ваша персональная реферальная ссылка: {url}
Вы уже пригласили {await get_referrals_count(session, message.from_user.id)} человек.

За одного приглашенного вы получите скидку 10% на Premium (скидка не суммируется за приглашенных людей)
Отправьте ссылку другу или нажмите кнопку ниж для быстрой отправки:""",
            reply_markup=referrer_keyboard(url),
            parse_mode="HTML",
        )
