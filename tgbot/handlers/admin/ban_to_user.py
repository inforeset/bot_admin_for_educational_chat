import asyncio

from aiogram import Dispatcher
from aiogram.types import Message, User
from aiogram.utils.exceptions import BadRequest
from aiogram.utils.markdown import hlink

from tgbot.config import Config
from tgbot.utils.chat_t import chat_types
from tgbot.utils.decorators import admin_and_bot_check, logging_message
from tgbot.utils.log_config import logger
from tgbot.utils.send_alert_to_admins import send_alert_to_admins


@logging_message
async def ban(message: Message, config: Config) -> None:
    """
    Хендлер для команды !b или !ban для роли ADMIN.
    Команда позволяет банить пользователя с описанием причины.
    Команду необходимо писать в ответе пересылаемого сообщения от того пользователя, которого нужно забанить.

    Handler for commands !b or !ban only for ADMIN.
    Command can be used for ban users with description of the reasons.
    You should write this command in response to a message from the user you want to ban.
    """

    reason_for_ban: str = " ".join(message.text.split()[1:])
    admin_who_banned: User = message.from_user
    user_was_banned: User = message.reply_to_message.from_user
    msg_id_del: int = int(message.reply_to_message.message_id)

    try:
        await message.bot.ban_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)
        logger.info("User {user} baned by {admin}".format(
            user=user_was_banned.id,
            admin=admin_who_banned.id)
        )

        chat_label: str = hlink(message.chat.title, await message.chat.get_url())
        text = "[ALERT] Администратор {admin} забанил пользователя {user} в чате {chat}. \nПричина: {reason}." \
               "\nСообщение за которое забанили: \n{reason_message}".format(
                admin=admin_who_banned.get_mention(),
                user=user_was_banned.get_mention(),
                chat=chat_label,
                reason=reason_for_ban,
                reason_message=message.reply_to_message.text)
        await send_alert_to_admins(message=message, text=text, config=config)
        logger.info("msg {msg_id_del} del by bot".format(
            msg_id_del=msg_id_del)
        )
        await message.bot.delete_message(message.chat.id, msg_id_del)

        await message.reply_to_message.answer(text=f'Пользователь {message.reply_to_message.from_user.get_mention()} '
                                                   f'<b>забанен</b> по причине: {reason_for_ban}')


    except BadRequest as e:
        logger.error("Failed to ban chat member: {error!r}", exc_info=e)
        await message.reply_to_message.answer(text=f'{message.from_user.get_mention()}, '
                                                   f'при выполнении команды возникла ошибка. Попробуйте еще раз.')


def register_bun(dp: Dispatcher) -> None:
    dp.register_message_handler(admin_and_bot_check(ban),
                                is_reply=True,
                                chat_type=chat_types(),
                                commands=["b", "ban"],
                                commands_prefix='!',
                                state="*",
                                is_admin=True)
