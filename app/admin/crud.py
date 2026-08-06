from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.models import AI, Message
from typing import Optional, List


async def set_ai_system_prompt(session: AsyncSession, text: str) -> bool:
    stmt = select(AI).order_by(desc(AI.id)).limit(1)
    result = await session.execute(stmt)
    ai = result.scalar_one_or_none()

    if not ai:
        return False

    ai.system_prompt = text

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
