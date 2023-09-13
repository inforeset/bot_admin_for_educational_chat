from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes, ReplyKeyboardRemove

from tgbot.utils.decorators import logging_message
from tgbot.utils.log_config import logger
from tgbot.utils.texts import greeting_text


@logging_message
async def new_member_info(message: Message) -> None:
    """
    Хендлер для приветствия нового пользователя группы с полезными ссылками.

    Handler for greeting new user in group and sending to him some useful links
    """

    bot_user = await message.bot.get_me()
    greeting: str = greeting_text(message=message, bot_user=bot_user)

    await message.answer(text=greeting, disable_web_page_preview=True, reply_markup=ReplyKeyboardRemove())
    logger.info("New User {user} was greeting".format(
        user=message.new_chat_members[0].id)
    )


def register_new_member_info(dp: Dispatcher):
    dp.register_message_handler(new_member_info, content_types=ContentTypes.NEW_CHAT_MEMBERS)
