import asyncio

from babel.dates import format_timedelta
from datetime import timedelta

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.utils.exceptions import BadRequest
from aiogram.utils.markdown import hlink

from tgbot.config import Config
from tgbot.utils.chat_t import chat_types
from tgbot.utils.decorators import admin_and_bot_check, logging_message
from tgbot.utils.log_config import logger
from tgbot.utils.send_alert_to_admins import send_alert_to_admins
from tgbot.utils.timedelta import parse_timedelta_from_message


@logging_message
async def ro(message: Message, config: Config) -> None:
    """
    Хендлер для команды !ro для роли ADMIN

    Команда позволяет перевести пользователя в режим "только чтение" с указанием продолжительности ограничения.
    Команду необходимо писать в ответе пересылаемого сообщения от того пользователя, которого нужно забанить.

    Command can be used for turning on mode read-only for users, you can write duration of this restriction.
    You should write this command in response to a message from the user you want to block.
    """

    duration: timedelta = await parse_timedelta_from_message(message)
    if not duration:
        return

    admin_who_restricted = message.from_user
    user_was_restricted = message.reply_to_message.from_user
    msg_id_del: int = int(message.reply_to_message.message_id)
    minute_delta: int = config.time_delta.minute_delta
    try:
        await message.chat.restrict(message.reply_to_message.from_user.id, can_send_messages=False, until_date=duration)
        logger.info("User {user} restricted by {admin} for {duration}".format(
            user=user_was_restricted.id,
            admin=admin_who_restricted.id,
            duration=duration)
        )

        chat_label: str = hlink(message.chat.title, await message.chat.get_url())
        text = "[ALERT] Администратор {admin} включил режим RO пользователю {user} в чате {chat} на {duration}.".format(
            admin=admin_who_restricted.get_mention(),
            user=user_was_restricted.get_mention(),
            chat=chat_label,
            duration=duration)
        await send_alert_to_admins(message=message, text=text, config=config)
        logger.info("msg {msg_id_del} del by bot".format(
            msg_id_del=msg_id_del)
        )
        await message.bot.delete_message(message.chat.id, msg_id_del)
        await message.reply_to_message.answer(
            "<b>Режим &#171;только чтениe&#187;</b> активирован для пользователя {user}."
            "\nПродолжительность: {duration}".format(
                user=message.reply_to_message.from_user.get_mention(),
                duration=format_timedelta(duration, locale='ru', granularity="second", format="short"))
        )

    except BadRequest as e:
        logger.error("Failed to restrict chat member: {error!r}", exc_info=e)


def register_ro(dp: Dispatcher) -> None:
    dp.register_message_handler(admin_and_bot_check(ro),
                                is_reply=True,
                                chat_type=chat_types(),
                                commands=["ro"],
                                commands_prefix='!',
                                state="*",
                                is_admin=True)
