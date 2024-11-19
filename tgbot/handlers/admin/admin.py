from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.utils.decorators import logging_message


@logging_message
async def admin_start(message: Message) -> None:
    """ Хендлер для команды start для роли ADMIN (префикс команды '/' или '!') """
    await message.answer('Привет, админ!')


def register_admin(dp: Dispatcher) -> None:
    dp.register_message_handler(admin_start, commands=["start"], commands_prefix='/!', state="*", is_admin=True)
