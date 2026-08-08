import asyncio

from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message
from app.echo.crud import (
    reset_user_requests,
    increment_user_request_limit,
    get_ai,
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


async def split_and_send_message(message: Message, text: str, max_length: int = 4000):
    if len(text) <= max_length:
        return await message.answer(text)

    # Разбиваем текст на части
    parts = []
    current_part = ""

    for line in text.split("\n"):
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + "\n"
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = line + "\n"

    if current_part:
        parts.append(current_part.strip())

    final_parts = []
    for part in parts:
        if len(part) <= max_length:
            final_parts.append(part)
        else:
            for i in range(0, len(part), max_length):
                final_parts.append(part[i : i + max_length])

    for i, part in enumerate(final_parts):
        if len(final_parts) > 1:
            part_text = f"📄 Часть {i + 1}/{len(final_parts)}\n\n{part}"
        else:
            part_text = part

        await message.answer(part_text, parse_mode=ParseMode.MARKDOWN_V2)

        # Небольшая задержка между отправками, чтобы избежать ограничений Telegram
        if i < len(final_parts) - 1:
            await asyncio.sleep(0.5)

    return None


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

        settings_ai = await get_ai(session)

        if user.premium or user.admin:
            if datetime.now() >= user.premium_end:
                return await message.answer("Ваш Premium закончился")

            ai = AI(
                prompt=message.text,
                system_prompt=settings_ai.system_prompt,
                qwen_use=settings_ai.qwen_use,
                history=user.messages,
                limit=100,
            )
            result = await ai.send()

            return await split_and_send_message(message, result)

        if user.request_limit is not None:
            if user.request_limit >= 3:
                if datetime.now() >= user.request_reload:
                    await reset_user_requests(session, user.telegram_id, 1)

                    ai = AI(
                        prompt=message.text,
                        system_prompt=settings_ai.system_prompt,
                        qwen_use=settings_ai.qwen_use,
                        history=user.messages,
                    )
                    result = await ai.send()

                    return await split_and_send_message(message, result)
                else:
                    return await message.answer(
                        "❌ У вас закончились запросы. Оформите Premium, чтобы продолжить общение или ждите следующего дня чтобы вернуть лимиты."
                    )

        ai = AI(
            prompt=message.text,
            system_prompt=settings_ai.system_prompt,
            qwen_use=settings_ai.qwen_use,
            history=user.messages,
        )
        result = await ai.send()

        await increment_user_request_limit(session, user.telegram_id)

        return await split_and_send_message(message, result)
