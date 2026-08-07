from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CopyTextButton,
    SwitchInlineQueryChosenChat,
)


def referrer_keyboard(url: str):
    builder = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Скопировать ссылку",
                    copy_text=CopyTextButton(text=url),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Отправить друзьям",
                    switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                        query=url,
                        allow_user_chats=True,
                        allow_group_chats=True,
                        allow_channel_chats=False,
                    ),
                ),
            ],
        ]
    )

    return builder
