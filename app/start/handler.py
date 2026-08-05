from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.start.crud import create_user
from app.start.keyboard import main_menu
from core.models import db_helper

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    async with db_helper.scoped_session_dependency() as session:
        await create_user(session, message.from_user.id, message.from_user.username)

    return await message.answer("Hello world", reply_markup=main_menu())
