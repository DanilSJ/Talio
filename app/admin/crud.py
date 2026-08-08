from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.models import AI, Message, User
from typing import Optional, List


async def set_ai_system_prompt(session: AsyncSession, text: str) -> bool:
    if not text or not text.strip():
        return False

    stmt = select(AI).order_by(desc(AI.id)).limit(1)
    result = await session.execute(stmt)
    ai = result.scalar_one_or_none()

    if not ai:
        # Создаем новый AI с промптом
        ai = AI(system_prompt=text.strip())
        session.add(ai)
    else:
        ai.system_prompt = text.strip()

    await session.commit()
    await session.refresh(ai)
    return True


async def set_on_off_qwen(session: AsyncSession) -> bool:
    stmt = select(AI).order_by(desc(AI.id)).limit(1)
    result = await session.execute(stmt)
    ai = result.scalar_one_or_none()
    print("dd")
    if not ai:
        print("xxxx")
        ai = AI(system_prompt="default", qwen_use=True)
        session.add(ai)
        await session.commit()
        await session.refresh(ai)
        return True
    else:
        print("zzz")
        if ai.qwen_use:
            ai.qwen_use = False
            await session.commit()
            await session.refresh(ai)
            return False
        else:
            ai.qwen_use = True
            await session.commit()
            await session.refresh(ai)
            return True


async def get_messages(session: AsyncSession) -> Optional[List[Message]]:
    stmt = select(Message)
    result = await session.execute(stmt)
    messages = result.scalars().all()

    if not messages:
        return None

    return list(messages)


async def get_users(session: AsyncSession):
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()

    if not users:
        return None

    return users
