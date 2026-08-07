import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from core.config import settings
from app import router

if settings.PROXY:
    session = AiohttpSession(proxy=settings.PROXY)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, session=session)
else:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
