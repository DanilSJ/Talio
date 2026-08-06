from aiogram import Router, F
from aiogram.types import Message
from app.echo.crud import (
    reset_user_requests,
    increment_user_request_limit,
    ai_system_prompt,
)
from app.start.crud import create_user
from app.echo.ai import AI
from core.models import db_helper
from datetime import datetime

router = Router()


@router.message(F.text)
async def echo(message: Message):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, message.from_user.id, message.from_user.username
        )

        system_prompt = await ai_system_prompt(session)

        if user.premium:
            ai = AI(
                prompt=message.text, system_prompt=system_prompt, history=user.messages
            )
            result = await ai.send()

            return message.answer(result)

        if user.request_limit >= 3:
            if datetime.now() >= user.request_reload:
                await reset_user_requests(session, user.telegram_id, 1)

                ai = AI(
                    prompt=message.text,
                    system_prompt=system_prompt,
                    history=user.messages,
                )
                result = await ai.send()

                return message.answer(result)
            else:
                return await message.answer(
                    "У вас закончились запросы оформите premium"
                )

        ai = AI(prompt=message.text, system_prompt=system_prompt, history=user.messages)
        result = await ai.send()

        await increment_user_request_limit(session, user.telegram_id)

        return message.answer(result)
