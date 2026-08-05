from aiogram import Router
from app.start.handler import router as start_router

router = Router()

router.include_router(start_router)
