import asyncio
from contextlib import suppress

from aiogram import Dispatcher
from aiogram.types import Message, ChatType, ReplyKeyboardRemove
from aiogram.utils.exceptions import TelegramAPIError

from tgbot.keyboards.reply.for_private import main_keyboard
from tgbot.utils.decorators import logging_message
from tgbot.utils.chat_t import chat_types


@logging_message
async def start_in_group(message: Message) -> None:
    """ Хендлер для команды start в группе (префикс команды '/' или '!') """

    msg_to_delete_in_30sec = await message.answer(f'{message.from_user.first_name}, эта команда для ЛС со мной!',
                                                  reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(30)
    with suppress(TelegramAPIError):
        await msg_to_delete_in_30sec.delete()
        await message.delete()


@logging_message
async def user_start(message: Message) -> None:
    """ Хендлер для команды start в ЛС (префикс команды '/' или '!') """

    await message.answer(f'Привет, {message.from_user.first_name}!', reply_markup=main_keyboard())


def register_user(dp: Dispatcher):
    dp.register_message_handler(start_in_group,
                                commands=["start"],
                                commands_prefix='/!',
                                chat_type=chat_types(),
                                state="*")
    dp.register_message_handler(user_start,
                                commands=["start"],
                                commands_prefix='/!',
                                chat_type=ChatType.PRIVATE,
                                state="*")