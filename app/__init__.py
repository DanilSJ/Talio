from aiogram import Router
from app.start.handler import router as start_router
from app.account.handler import router as account_router
from app.payment.handler import router as payment_router
from app.questions.handler import router as questions_router
from app.terms.handler import router as terms_router
from app.admin.handler import router as admin_router
from app.referrer.handler import router as referrer_router
from app.echo.handler import router as echo_router

router = Router()

router.include_router(start_router)
router.include_router(account_router)
router.include_router(payment_router)
router.include_router(questions_router)
router.include_router(terms_router)
router.include_router(admin_router)
router.include_router(referrer_router)
router.include_router(echo_router)
