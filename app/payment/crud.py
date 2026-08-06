from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import User


async def update_premium(
    session: AsyncSession,
    telegram_id: int,
) -> Optional[User]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.premium = True
    user.buy_premium = datetime.now()

    await session.commit()
    await session.refresh(user)

    return user

async def del_referrer(
    session: AsyncSession,
    telegram_id: int,
) -> Optional[User]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.referrer_is_active = False

    await session.commit()
    await session.refresh(user)

    return user
