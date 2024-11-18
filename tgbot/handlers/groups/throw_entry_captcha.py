from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.utils.capcha import throw_capcha
from tgbot.utils.decorators import logging_message
from tgbot.config import Config


@logging_message
async def handler_throw_capcha(message: Message, config: Config) -> None:
    """Handler for generate captcha image to user
           param message: Message
           return None
    """
    await throw_capcha(message=message, config=config)


def register_capcha(dp: Dispatcher) -> None:
    dp.register_message_handler(handler_throw_capcha,
                                commands=['capcha'],
                                commands_prefix='!/',
                                state="*")