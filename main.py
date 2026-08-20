import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from app.echo.crud import get_inactive_users
from core.config import settings
from app import router
from core.models import db_helper

if settings.PROXY:
    session = AiohttpSession(proxy=settings.PROXY)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, session=session)
else:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

dp = Dispatcher()

# Словарь для хранения времени последнего отправленного сообщения
# Ключ: telegram_id, Значение: datetime последнего отправления
last_message_time = {}


async def background_task():
    while True:
        async with db_helper.scoped_session_dependency() as session:
            try:
                users = await get_inactive_users(session)
                current_time = datetime.now()

                for el in users:
                    user_id = el.telegram_id

                    # Проверяем, отправляли ли мы сообщение этому пользователю
                    if user_id in last_message_time:
                        # Если отправляли, проверяем прошло ли 3 дня (72 часа)
                        time_diff = current_time - last_message_time[user_id]
                        if time_diff < timedelta(days=3):
                            # Если прошло меньше 3 дней - пропускаем
                            continue

                    # Отправляем сообщение
                    await bot.send_message(
                        chat_id=user_id,
                        text="Привет! Как твои дела, как успехи, нужна ли какая-то помощь? Не останавливайся и не сдавайся у тебя обязательно все получится!",
                    )

                    # Обновляем время отправки в словаре
                    last_message_time[user_id] = current_time

                await asyncio.sleep(360)  # Проверка каждые 6 минут

            except Exception as e:
                print(f"Ошибка в background_task: {e}")
                await asyncio.sleep(60)  # При ошибке ждем минуту


async def main():
    dp.include_router(router)
    await asyncio.gather(dp.start_polling(bot), background_task())


if __name__ == "__main__":
    asyncio.run(main())
