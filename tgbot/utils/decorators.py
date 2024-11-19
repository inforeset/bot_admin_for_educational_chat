from functools import wraps
from typing import Callable, Any

from aiogram.types import Message

from tgbot.filters.admin import AdminFilter
from tgbot.utils.log_config import logger
from tgbot.utils.update_log import add_to_log_message


def admin_and_bot_check(func: Callable) -> Callable:
    """ Декоратор для хендлера, который не позволяет наложить ограничение (бан или "только чтение") на бота, владельца
    или администратора чата """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        message: Message = args[0]

        is_bot: bool = message.reply_to_message.from_user.is_bot
        is_admin: bool = await AdminFilter.check(message.reply_to_message)

        if not is_admin and not is_bot:
            return await func(*args, **kwargs)

        await message.reply_to_message.answer(text=f'{message.from_user.get_mention()}, '
                                                   f'вы не можете ограничить бота, владельца или администратора чата!')

    return wrapper


def logging_message(func: Callable) -> Callable:
    @wraps(func)
    async def wrapped_func(*args, **kwargs) -> Any:
        try:
            if args:
                message: Message = args[0]
                await add_to_log_message(message=message)
        except IndexError as exc:
            logger.error('Function name: {func.__name__}', exc_info=exc)
        return await func(*args, **kwargs)
    return wrapped_func
