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
from datetime import datetime, timedelta

router = Router()

user_last_message = {}
MESSAGE_COOLDOWN = 2
MAX_MESSAGES_PER_MINUTE = 10
user_message_count = {}
user_message_reset = {}


@router.message(F.text)
async def echo(message: Message):
    user_id = message.from_user.id
    current_time = datetime.now()

    if user_id in user_last_message:
        time_diff = (current_time - user_last_message[user_id]).total_seconds()
        if time_diff < MESSAGE_COOLDOWN:
            await message.answer(
                "⚠️ Пожалуйста, не спамьте! Подождите немного перед отправкой следующего сообщения."
            )
            return

    if user_id not in user_message_count:
        user_message_count[user_id] = 1
        user_message_reset[user_id] = current_time + timedelta(minutes=1)
    else:
        if current_time >= user_message_reset[user_id]:
            user_message_count[user_id] = 1
            user_message_reset[user_id] = current_time + timedelta(minutes=1)
        else:
            user_message_count[user_id] += 1
            if user_message_count[user_id] > MAX_MESSAGES_PER_MINUTE:
                await message.answer(
                    "🚫 Превышен лимит сообщений в минуту! Пожалуйста, подождите немного."
                )
                return

    user_last_message[user_id] = current_time

    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, message.from_user.id, message.from_user.username
        )

        system_prompt = await ai_system_prompt(session)

        if user.premium:
            if datetime.now() >= user.premium_end:
                return await message.answer("Ваш Premium закончился")

            ai = AI(
                prompt=message.text,
                system_prompt=system_prompt,
                history=user.messages,
                limit=100,
            )
            result = await ai.send()

            return await message.answer(result)

        if user.request_limit is not None:
            if user.request_limit >= 3:
                if datetime.now() >= user.request_reload:
                    await reset_user_requests(session, user.telegram_id, 1)

                    ai = AI(
                        prompt=message.text,
                        system_prompt=system_prompt,
                        history=user.messages,
                    )
                    result = await ai.send()

                    return await message.answer(result)
                else:
                    return await message.answer(
                        "❌ У вас закончились запросы. Оформите Premium, чтобы продолжить общение."
                    )

        ai = AI(
            prompt=message.text,
            system_prompt=system_prompt,
            history=user.messages,
        )
        result = await ai.send()

        await increment_user_request_limit(session, user.telegram_id)

        return await message.answer(result)
