from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import User


async def get_referrals_count(
    session: AsyncSession,
    telegram_id: int,
) -> int:
    stmt = (
        select(User)
        .where(User.telegram_id == telegram_id)
        .options(selectinload(User.referred_users))
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return 0

    return len(user.referred_users)
