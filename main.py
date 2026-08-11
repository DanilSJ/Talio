import asyncio
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


async def background_task():
    while True:
        async with db_helper.scoped_session_dependency() as session:
            try:
                users = await get_inactive_users(session)
                for el in users:
                    await bot.send_message(
                        chat_id=el.telegram_id,
                        text="Привет! Как твои дела, как успехи, нужна ли какая-то помощь? Не останавливайся и не сдавайся, мы обязательно придем к нужным результатам!",
                    )
                await asyncio.sleep(360)
            except Exception as e:
                print(f"3 day:  {e}")


async def main():
    dp.include_router(router)
    await asyncio.gather(dp.start_polling(bot), background_task())


if __name__ == "__main__":
    asyncio.run(main())
