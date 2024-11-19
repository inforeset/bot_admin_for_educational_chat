import asyncio
from contextlib import suppress

from aiogram import md, types, Dispatcher
from aiogram.utils.exceptions import TelegramAPIError

from tgbot.config import Config
from tgbot.utils.admin_ids import get_admins_ids_for_help_and_paste
from tgbot.utils.chat_t import chat_types
from tgbot.utils.decorators import logging_message
from tgbot.utils.hastebin import get_hastebin_client


@logging_message
async def command_paste(message: types.Message, config: Config) -> None:
    """
    Хендлер для комманды /paste.
    Используется для вставки сообщения на hastebin сервер.

    Handler for command /paste.
    Can be used for sending message to hastebin server.

    :param message: объект сообщения от пользователя;
    :param config: параметр из одноименного класса Config
    """

    by_admin: bool = message.from_user.id in await get_admins_ids_for_help_and_paste(message=message)
    by_message_owner: bool = message.from_user.id is message.reply_to_message.from_user.id

    if not by_admin or by_message_owner:
        msg_to_delete_in_30sec = await message.reply(
            'Только владелец сообщения или администраторы могут отправить сообщение на hastebin-сервер')
        await asyncio.sleep(30)
        with suppress(TelegramAPIError):
            await msg_to_delete_in_30sec.delete()
            await message.delete()

        return

    content: str = message.reply_to_message.text or message.reply_to_message.caption
    messages_to_delete: list[types.Message] = []

    # на сообщение от бота
    if message.reply_to_message.from_user.id == message.bot.id:
        messages_to_delete.append(message)
        await message.answer(f'{message.from_user.get_mention()}, '
                             f'cообщения бота нельзя отправлять на HasteBin!')

    # на короткое сообщение
    elif len(content) < 30 and content.count('\n') < 2:
        messages_to_delete.append(message)
        await message.answer(f'{message.from_user.get_mention()}, '
                             f'это сообщение слишком короткое для отправки кода на HasteBin!')

    else:
        messages_to_delete.append(message.reply_to_message)
        messages_to_delete.append(message)
        encoding_content: bytes = content.encode()
        response: dict = await get_hastebin_client(config.misc.hastebin_url).create_document(encoding_content)
        document_url: str = get_hastebin_client(config.misc.hastebin_url).format_url(response["key"])
        text: str = ("Сообщение опубликованное {author} было перемещено в {url}\n"
                     "Размер: {size} байт".format(author=message.reply_to_message.from_user.get_mention(as_html=True),
                                                  url=md.hlink("HasteBin", document_url),
                                                  size=len(encoding_content),
                                                  )
                     )

        await message.answer(text, allow_sending_without_reply=True)

    for i_message in messages_to_delete:
        with suppress(TelegramAPIError):
            await i_message.delete()


def register_paste_command(dp: Dispatcher):
    dp.register_message_handler(command_paste,
                                is_reply=True,
                                chat_type=chat_types(),
                                commands=['paste'],
                                commands_prefix='!/',
                                state='*')
