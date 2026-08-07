from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import User, UserReferral


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


async def deactivate_referrer(
    session: AsyncSession,
    user_telegram_id: int,
    referrer_telegram_id: Optional[int] = None,
) -> bool:
    """Деактивировать реферера у пользователя"""
    # Получаем пользователя
    stmt_user = select(User).where(User.telegram_id == user_telegram_id)
    result_user = await session.execute(stmt_user)
    user = result_user.scalar_one_or_none()

    if not user:
        return False

    # Базовый запрос для деактивации
    stmt = select(UserReferral).where(
        UserReferral.user_id == user.id, UserReferral.is_active == True
    )

    # Если указан конкретный реферер
    if referrer_telegram_id:
        stmt_referrer = select(User).where(User.telegram_id == referrer_telegram_id)
        result_referrer = await session.execute(stmt_referrer)
        referrer = result_referrer.scalar_one_or_none()

        if not referrer:
            return False

        stmt = stmt.where(UserReferral.referrer_id == referrer.id)

    result = await session.execute(stmt)
    referral = result.scalar_one_or_none()

    if not referral:
        return False

    referral.is_active = False
    await session.commit()
    return True


async def deactivate_all_referrers(session: AsyncSession, user_telegram_id: int) -> int:
    """Деактивировать всех рефереров пользователя"""
    stmt_user = select(User).where(User.telegram_id == user_telegram_id)
    result_user = await session.execute(stmt_user)
    user = result_user.scalar_one_or_none()

    if not user:
        return 0

    # Обновляем все активные связи
    stmt = select(UserReferral).where(
        UserReferral.user_id == user.id, UserReferral.is_active == True
    )
    result = await session.execute(stmt)
    referrals = result.scalars().all()

    count = len(referrals)
    for referral in referrals:
        referral.is_active = False

    await session.commit()
    return count


async def get_active_referrer(
    session: AsyncSession, user_telegram_id: int
) -> Optional[User]:
    """Получить первого активного реферера пользователя"""
    stmt_user = select(User).where(User.telegram_id == user_telegram_id)
    result_user = await session.execute(stmt_user)
    user = result_user.scalar_one_or_none()

    if not user:
        return None

    # Ищем активную связь
    stmt = (
        select(UserReferral)
        .where(UserReferral.user_id == user.id, UserReferral.is_active == True)
        .limit(1)
    )
    result = await session.execute(stmt)
    referral = result.scalar_one_or_none()

    if not referral:
        return None

    # Получаем данные реферера
    stmt_referrer = select(User).where(User.id == referral.referrer_id)
    result_referrer = await session.execute(stmt_referrer)
    return result_referrer.scalar_one_or_none()


async def get_all_active_referrers(
    session: AsyncSession, user_telegram_id: int
) -> List[User]:
    """Получить всех активных рефереров пользователя"""
    stmt_user = select(User).where(User.telegram_id == user_telegram_id)
    result_user = await session.execute(stmt_user)
    user = result_user.scalar_one_or_none()

    if not user:
        return []

    # Ищем все активные связи
    stmt = select(UserReferral).where(
        UserReferral.user_id == user.id, UserReferral.is_active == True
    )
    result = await session.execute(stmt)
    referrals = result.scalars().all()

    if not referrals:
        return []

    # Получаем всех рефереров
    referrer_ids = [r.referrer_id for r in referrals]
    stmt_referrers = select(User).where(User.id.in_(referrer_ids))
    result_referrers = await session.execute(stmt_referrers)
    return result_referrers.scalars().all()


async def has_active_referrer(session: AsyncSession, user_telegram_id: int) -> bool:
    """Проверить наличие активного реферера у пользователя"""
    stmt_user = select(User).where(User.telegram_id == user_telegram_id)
    result_user = await session.execute(stmt_user)
    user = result_user.scalar_one_or_none()

    if not user:
        return False

    stmt = select(UserReferral).where(
        UserReferral.user_id == user.id, UserReferral.is_active == True
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def get_referred_users(
    session: AsyncSession, referrer_telegram_id: int, only_active: bool = True
) -> List[User]:
    """Получить пользователей, которых пригласил реферер"""
    stmt_referrer = select(User).where(User.telegram_id == referrer_telegram_id)
    result_referrer = await session.execute(stmt_referrer)
    referrer = result_referrer.scalar_one_or_none()

    if not referrer:
        return []

    # Запрос на получение рефералов
    stmt = select(UserReferral).where(UserReferral.referrer_id == referrer.id)

    if only_active:
        stmt = stmt.where(UserReferral.is_active == True)

    result = await session.execute(stmt)
    referrals = result.scalars().all()

    if not referrals:
        return []

    # Получаем всех пользователей
    user_ids = [r.user_id for r in referrals]
    stmt_users = select(User).where(User.id.in_(user_ids))
    result_users = await session.execute(stmt_users)
    return result_users.scalars().all()


async def get_referral_stats(session: AsyncSession, user_telegram_id: int) -> dict:
    """Получить статистику по рефералам пользователя"""
    stmt_user = select(User).where(User.telegram_id == user_telegram_id)
    result_user = await session.execute(stmt_user)
    user = result_user.scalar_one_or_none()

    if not user:
        return {}

    # Кого пригласил пользователь
    stmt_referred = select(UserReferral).where(UserReferral.referrer_id == user.id)
    result_referred = await session.execute(stmt_referred)
    all_referrals = result_referred.scalars().all()

    total_referred = len(all_referrals)
    active_referred = len([r for r in all_referrals if r.is_active])

    # Кто пригласил пользователя (активные)
    stmt_referrers = select(UserReferral).where(
        UserReferral.user_id == user.id, UserReferral.is_active == True
    )
    result_referrers = await session.execute(stmt_referrers)
    active_referrers = result_referrers.scalars().all()

    # Получаем список активных рефереров
    referrer_list = []
    if active_referrers:
        referrer_ids = [r.referrer_id for r in active_referrers]
        stmt_users = select(User).where(User.id.in_(referrer_ids))
        result_users = await session.execute(stmt_users)
        referrer_list = result_users.scalars().all()

    # Премиум рефералы
    referred_user_ids = [r.user_id for r in all_referrals]
    if referred_user_ids:
        stmt_premium = select(User).where(
            User.id.in_(referred_user_ids), User.premium == True
        )
        result_premium = await session.execute(stmt_premium)
        premium_referred = result_premium.scalars().all()
    else:
        premium_referred = []

    return {
        "total_referred": total_referred,
        "active_referred": active_referred,
        "premium_referred": len(premium_referred),
        "active_referrers": len(active_referrers),
        "referrer_list": referrer_list,
        "referrer_count": len(active_referrers),
    }
