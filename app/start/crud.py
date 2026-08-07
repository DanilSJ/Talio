from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import User
from core.models.user import UserReferral


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
) -> User:
    stmt = (
        select(User)
        .where(User.telegram_id == telegram_id)
        .options(selectinload(User.referred_users))
        .options(selectinload(User.messages))
    )
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if username and existing_user.username != username:
            existing_user.username = username
            await session.commit()
            await session.refresh(existing_user)
        return existing_user

    user = User(
        telegram_id=telegram_id,
        username=username,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


async def add_referrer(
    session: AsyncSession,
    user_telegram_id: int,
    referrer_telegram_id: int,
) -> Optional[User]:
    if user_telegram_id == referrer_telegram_id:
        return None

    stmt_user = select(User).where(User.telegram_id == user_telegram_id)
    result_user = await session.execute(stmt_user)
    user = result_user.scalar_one_or_none()

    if not user:
        return None

    stmt_referrer = select(User).where(User.telegram_id == referrer_telegram_id)
    result_referrer = await session.execute(stmt_referrer)
    referrer = result_referrer.scalar_one_or_none()

    if not referrer:
        return None

    stmt_existing = select(UserReferral).where(
        UserReferral.user_id == user.id, UserReferral.referrer_id == referrer.id
    )
    result_existing = await session.execute(stmt_existing)
    existing = result_existing.scalar_one_or_none()

    if existing:
        if not existing.is_active:
            existing.is_active = True
            await session.commit()
            return user
        return None

    referral = UserReferral(user_id=referrer.id, referrer_id=user.id, is_active=True)

    session.add(referral)
    await session.commit()

    await session.refresh(user)
    await session.refresh(referrer)

    return user
