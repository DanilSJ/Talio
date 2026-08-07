from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.models import User, AI


async def update_user_request_limits(
    session: AsyncSession,
    telegram_id: int,
    request_limit: Optional[int] = None,
    request_reload: Optional[datetime] = None,
) -> Optional[User]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    if request_limit is not None:
        user.request_limit = request_limit

    if request_reload is not None:
        user.request_reload = request_reload

    await session.commit()
    await session.refresh(user)

    return user


async def reset_user_requests(
    session: AsyncSession,
    telegram_id: int,
    new_limit: int,
) -> Optional[User]:
    reload_time = datetime.now() + timedelta(days=1)

    return await update_user_request_limits(
        session=session,
        telegram_id=telegram_id,
        request_limit=new_limit,
        request_reload=reload_time,
    )


async def increment_user_request_limit(
    session: AsyncSession,
    telegram_id: int,
) -> Optional[User]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or user.request_limit is None:
        return None

    user.request_limit = user.request_limit + 1

    await session.commit()
    await session.refresh(user)

    return user


async def ai_system_prompt(session: AsyncSession) -> str:
    stmt = select(AI.system_prompt).order_by(desc(AI.id)).limit(1)
    result = await session.execute(stmt)
    system_prompt = result.scalar_one_or_none()

    return system_prompt if system_prompt is not None else "default_prompt"


async def deactivate_premium(
    session: AsyncSession,
    telegram_id: int,
) -> Optional[User]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.premium = False

    await session.commit()
    await session.refresh(user)

    return user
