import asyncio
from contextlib import suppress

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.utils.exceptions import TelegramAPIError

from tgbot.utils.decorators import logging_message


@logging_message
async def answer_for_incorrect_using_commands(message: Message):
    msg_to_delete_in_15sec = await message.reply('Эта команда должна вводиться в ответ на сообщение!')

    with suppress(TelegramAPIError):
        await asyncio.sleep(30)
        await msg_to_delete_in_15sec.delete()
        await message.delete()


def register_incorrect_using_command(dp: Dispatcher):
    dp.register_message_handler(answer_for_incorrect_using_commands,
                                is_reply=False,
                                commands=['ro', 'ban', 'b', 'report', 'paste'],
                                commands_prefix='!/',
                                state='*')