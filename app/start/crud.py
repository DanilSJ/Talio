from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import User


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id).options(selectinload(User.referred_users))
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
    invited_telegram_id: int,
    referrer_telegram_id: int,
) -> Optional[User]:
    stmt_referrer = select(User).where(User.telegram_id == referrer_telegram_id)
    result_referrer = await session.execute(stmt_referrer)
    referrer = result_referrer.scalar_one_or_none()

    if not referrer:
        return None

    stmt_invited = select(User).where(User.telegram_id == invited_telegram_id)
    result_invited = await session.execute(stmt_invited)
    invited_user = result_invited.scalar_one_or_none()

    if not invited_user:
        return None

    if invited_user.referrer_id is not None:
        return None

    if invited_telegram_id == referrer_telegram_id:
        return None

    invited_user.referrer_id = referrer.id
    invited_user.referrer_is_active = True

    await session.commit()

    await session.refresh(invited_user)
    await session.refresh(referrer)

    return invited_user
