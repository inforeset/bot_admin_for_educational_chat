import asyncio
from contextlib import suppress

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation, TelegramAPIError

from tgbot.utils.admin_ids import get_admins_ids_for_help_and_paste
from tgbot.utils.chat_t import chat_types
from tgbot.utils.decorators import logging_message
from tgbot.utils.help_text import choice_for_helping_text
from tgbot.utils.log_config import logger


@logging_message
async def help_command(message: Message) -> None:
    """
        Хендлер для команды !help

        Команда позволяет высылать список полезных ссылок пользователю в диалог с ботом (для юзера) ИЛИ синтаксис
        администраторских команд (для админа).
        Команду можно писать как в группе, так и в ЛС боту от любой роли.

        В случаях если диалог с ботом не был инициализирован пользователем или бот был приостановлен, то пользователю
        высылается соответствующее сообщение.

        Command can be used for getting different useful links for users or commands syntax for admins.
        Command can be writen in Private chat or in Group
        """

    admins_ids: list[int] = await get_admins_ids_for_help_and_paste(message=message)
    helping_text: str = await choice_for_helping_text(message, admins_ids)
    bot_user = await message.bot.get_me()
    messages_to_delete_in_15_sec: list[Message] = []

    try:
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text=helping_text,
                                       disable_web_page_preview=True)
        logger.info("Bot send to user {user} help-message".format(
            user=message.from_user.id)
        )

    except BotBlocked as e:
        logger.error("Failed to send help-message to User {user}: {error!r}".format(
            user=message.from_user.id,
            error=e)
        )
        delete_this_msg = await message.reply(
            f'Я не могу написать вам, т.к. вы приостановили диалог со мной.\n'
            f'Возобновите диалог и попробуйте снова:\n'
            f'@{bot_user.username}')
        messages_to_delete_in_15_sec.append(delete_this_msg)

    except CantInitiateConversation as e:
        logger.error("Failed to send help-message to User {user}: {error!r}".format(
            user=message.from_user.id,
            error=e)
        )
        delete_this_msg = await message.reply(
            f'Я не могу написать вам, т.к. вы не инициализировали диалог со мной.\n'
            f'Отправьте команду <i>/start</i> мне в ЛС:\n'
            f'@{bot_user.username}')
        messages_to_delete_in_15_sec.append(delete_this_msg)

    finally:
        with suppress(TelegramAPIError):
            await message.delete()
        if messages_to_delete_in_15_sec:
            await asyncio.sleep(15)
            for msg_to_delete in messages_to_delete_in_15_sec:
                with suppress(TelegramAPIError):
                    await msg_to_delete.delete()


def register_help_command(dp: Dispatcher):
    dp.register_message_handler(help_command,
                                chat_type=chat_types(),
                                commands=['help'],
                                commands_prefix='!/',
                                state='*')