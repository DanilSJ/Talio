from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.questions.keyboard import questions_menu

router = Router()


@router.message(F.text == "❓ Вопрос-ответ")
async def questions(message: Message):
    return await message.answer(
        "Выберите интересующий вас вопрос из списка ниже:",
        reply_markup=questions_menu(),
    )


@router.callback_query(F.data == "question_1")
async def question_1(callback: CallbackQuery):
    await callback.answer(
        """*TALIO* - то AI-система по раскрытию и монетизации вашего потенциала.

У каждого человека есть активы, которые остаются нераскрытыми. Наш ассистент помогает обнаружить их, развить и превратить в возможности.

*TALIO* анализирует ваши способности, опыт и интересы, чтобы найти направления, где вы можете создавать максимальную ценность.

По сути это ваш коуч с искусственным интеллектом, работающий без сна и отдыха 24/7.""",
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "question_2")
async def question_2(callback: CallbackQuery):
    await callback.answer(
        """Да! Конфиденциальность - главное правило. Всё общение строго приватно, переписка доступна только вам.""",
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "question_3")
async def question_3(callback: CallbackQuery):
    await callback.answer(
        """Нет! Бот не предоставляет профессиональных консультаций. Он является отличной первой поддержкой - выслушает, даст задание, поможет выразить мысли, подскажет идеи, даст направление и мотивацию. Но никакая нейросеть не сможет заменить настоящего специалиста.""",
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "question_4")
async def question_4(callback: CallbackQuery):
    await callback.answer(
        """Да, в обычной версии вам доступно 3 сообщения в сутки – этого достаточно, чтобы получить правильное направление в раскрытии своего потенциала и принять решение о приобретении полноценной версии нашего ассистента.""",
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "question_5")
async def question_5(callback: CallbackQuery):
    await callback.answer(
        """Premium снимает лимит на количество сообщений и подключает к работе более мощную нейросеть.

Эта версия ассистента уже более продвинута и заточена на результат.

Premium дает полноценное общение, помощь и поддержку в любое удобное время 24/7.

Стоимость Premium-подписки составляет 500 рублей в месяц.""",
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "question_6")
async def question_6(callback: CallbackQuery):
    await callback.answer(
        """Просто спроси в чате: «До какого числа у меня подписка?» - бот сообщит, сколько осталось дней. Или загляни в «Личный кабинет» - там находится вся информация по твоему аккаунту.""",
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "question_7")
async def question_7(callback: CallbackQuery):
    await callback.answer(
        """Вопросы, пожелания, идеи и сообщения об ошибках - @AssistantKingdomBot""",
        parse_mode="Markdown",
    )
