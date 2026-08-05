import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from core.config import settings

session = AiohttpSession(proxy=settings.PROXY)
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, session=session)

dp = Dispatcher()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
