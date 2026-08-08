from collections import Counter
from datetime import datetime, timedelta, timezone
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app.admin.crud import (
    set_ai_system_prompt,
    get_messages,
    get_users,
    set_on_off_qwen,
)
from app.admin.keyboard import admin_keyboard
from app.admin.state import AdminSystemPromptState, AdminADSState
from app.echo.crud import get_ai
from app.start.crud import create_user
from core.models import db_helper

router = Router()
MSK = timezone(timedelta(hours=3))


@router.message(Command("admin"))
async def admin(message: Message):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, message.from_user.id, message.from_user.username
        )

        if not user.admin:
            return None

        return await message.answer(
            "Админ панель:",
            reply_markup=admin_keyboard(),
        )


@router.callback_query(F.data == "admin_set_system_prompt")
async def admin_system_prompt(callback: CallbackQuery, state: FSMContext):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, callback.from_user.id, callback.from_user.username
        )
        if not user.admin:
            return None

        ai = await get_ai(session)

        await callback.message.answer(f"Текст в данный момент: {ai.system_prompt}")
        await callback.message.answer(
            "Напишите текст который будет в системном промпте"
        )
        await state.set_state(AdminSystemPromptState.text)


@router.message(F.text, AdminSystemPromptState.text)
async def admin_set_system_prompt(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, message.from_user.id, message.from_user.username
        )
        if not user.admin:
            return None

        await set_ai_system_prompt(session, message.text)
        await state.clear()
        return await message.answer("Системный промпт успешно изменен")


@router.callback_query(F.data == "admin_ads")
async def admin_ads(callback: CallbackQuery, state: FSMContext):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, callback.from_user.id, callback.from_user.username
        )
        if not user.admin:
            return None

        await callback.message.answer("Напишите текст который будет рассылаться")
        await state.set_state(AdminADSState.text)


@router.message(AdminADSState.text)
async def admin_send_ads(message: Message, state: FSMContext):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, message.from_user.id, message.from_user.username
        )
        if not user.admin:
            return None

        # Получаем всех пользователей
        users = await get_users(session)

        for user in users:
            try:
                await message.copy_to(chat_id=user.telegram_id)
            except Exception as e:
                print(f"Ошибка при отправке пользователю {user.telegram_id}: {e}")
                continue

        await state.clear()
        return await message.answer("Рассылка была отправлена")


@router.callback_query(F.data == "admin_messages")
async def admin_ads(callback: CallbackQuery):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, callback.from_user.id, callback.from_user.username
        )
        if not user.admin:
            return None

        messages = await get_messages(session)

        if not messages:
            stats_text = "📊 В базе пока нет сообщений"
            return await callback.message.answer(stats_text)

        stats = calculate_stats(messages)

        stats_text = (
            f"📊 Статистика сообщений:\n\n"
            f"📅 За сегодня: {stats['today_count']} сообщений\n"
            f"📆 За неделю: {stats['week_count']} сообщений\n"
            f"📈 Всего: {stats['total_count']} сообщений\n\n"
            f"🏆 Топ активных участников (за неделю):\n"
        )

        if stats["top_users"]:
            for i, (username, count) in enumerate(stats["top_users"].items(), 1):
                stats_text += f"{i}. @{username} — {count} сообщений\n"
        else:
            stats_text += "За неделю нет сообщений"

        await callback.message.answer(stats_text)

        return await callback.message.answer("Напишите текст который будет рассылаться")


def calculate_stats(messages):
    now = datetime.now(MSK)
    today_start = datetime(now.year, now.month, now.day, tzinfo=MSK)
    week_ago = now - timedelta(days=7)

    today_count = 0
    week_count = 0
    week_users = Counter()

    for msg in messages:
        if msg.create_at >= today_start:
            today_count += 1

        if msg.create_at >= week_ago:
            week_count += 1
            if msg.user and msg.user.username:
                week_users[msg.user.username] += 1

    top_users = dict(week_users.most_common(10))

    return {
        "today_count": today_count,
        "week_count": week_count,
        "total_count": len(messages),
        "top_users": top_users,
    }


@router.callback_query(F.data == "on_off_qwen")
async def on_off_qwen(callback: CallbackQuery):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, callback.from_user.id, callback.from_user.username
        )
        if not user.admin:
            return None
        result = await set_on_off_qwen(session)

        if result:
            return await callback.message.answer("QWEN был включен")
        else:
            return await callback.message.answer("QWEN был отключен")


@router.callback_query(F.data == "how_users")
async def how_users(callback: CallbackQuery):
    async with db_helper.scoped_session_dependency() as session:
        user = await create_user(
            session, callback.from_user.id, callback.from_user.username
        )
        if not user.admin:
            return None
        result = await get_users(session)

        return await callback.message.answer(f"Пользователей: {len(result)}")
