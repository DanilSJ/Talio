from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.start.crud import create_user, add_referrer
from app.start.keyboard import main_menu
from core.models import db_helper

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    args = message.text.split()
    referrer_id = None

    if len(args) > 1:
        try:
            referrer_id = int(args[1])
        except ValueError:
            referrer_id = None

    async with db_helper.scoped_session_dependency() as session:
        await create_user(session, message.from_user.id, message.from_user.username)

        if referrer_id:
            await add_referrer(session, message.from_user.id, referrer_id)

    return await message.answer(
        """Приветствую вас, дорогой друг! 😊

Меня зовут <b>TALIO</b>, я ваш нейро-ассистент по раскрытию и монетизации потенциала.

Я проанализирую ваши способности, опыт и интересы, чтобы найти направления, где вы можете создавать максимальную ценность.

Подробнее ознакомиться со мной вы можете в <b>Меню во вкладке</b> <b>«Вопрос-ответ»</b>.

Давайте начнем это увлекательное путешествие в познании себя и приобретении дохода через те сильные качества, которые у вас <b>уже есть!</b>

Верю в вас! 😊""",
        reply_markup=main_menu(),
    )
