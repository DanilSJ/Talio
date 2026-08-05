from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.start.keyboard import main_menu

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Hello world", reply_markup=main_menu())
