from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from core.models import User, AI, Message


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

    if not user:
        return None

    if user.request_limit is None:
        user.request_limit = 1
    else:
        user.request_limit = user.request_limit + 1

    user.request_reload = datetime.now() + timedelta(days=1)

    await session.commit()
    await session.refresh(user)

    return user


async def get_ai(session: AsyncSession):
    stmt = select(AI).order_by(desc(AI.id)).limit(1)
    result = await session.execute(stmt)
    ai = result.scalar_one_or_none()

    return ai


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


async def create_user_message(
    session: AsyncSession,
    telegram_id: int,
    question: str,
    answer: Optional[str] = None,
) -> Optional[Message]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Создаем новое сообщение
    new_message = Message(
        question=question,
        answer=answer,
        user_id=user.id,
    )

    session.add(new_message)
    await session.commit()
    await session.refresh(new_message)

    return new_message


async def get_inactive_users(session: AsyncSession, days_threshold: int = 3):
    """
    Получает пользователей, которые не создавали сообщения более указанного количества дней.

    Args:
        session: Асинхронная сессия SQLAlchemy
        days_threshold: Количество дней бездействия (по умолчанию 3)

    Returns:
        List[User]: Список пользователей, не писавших более days_threshold дней
    """
    # Вычисляем дату, которая была days_threshold дней назад
    threshold_date = datetime.now() - timedelta(days=days_threshold)

    # Правильный запрос с использованием Message.created_at
    stmt = (
        select(User)
        .outerjoin(Message, User.id == Message.user_id)  # Явный JOIN
        .group_by(User.id)
        .having(
            func.max(Message.create_at)
            < threshold_date  # Используем Message.created_at
        )
    )

    result = await session.execute(stmt)
    inactive_users = result.scalars().all()

    return inactive_users
