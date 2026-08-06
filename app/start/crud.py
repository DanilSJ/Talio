from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
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


async def add_referrer(
    session: AsyncSession,
    telegram_id: int,
    referrer_id: int,
) -> Optional[User]:
    stmt = select(User).where(User.telegram_id == referrer_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    stmt_referrer = select(User).where(User.telegram_id == telegram_id)
    result_referrer = await session.execute(stmt_referrer)
    referrer = result_referrer.scalar_one_or_none()

    if not referrer:
        return None

    user.referrer_id = referrer.id
    user.referrer_is_active = True

    await session.commit()
    await session.refresh(user)

    return user
