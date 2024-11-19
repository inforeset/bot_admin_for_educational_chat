from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.utils.markdown import hlink

from tgbot.config import Config
from tgbot.utils.chat_t import chat_types
from tgbot.utils.decorators import logging_message
from tgbot.utils.log_config import logger
from tgbot.utils.send_alert_to_admins import send_alert_to_admins


@logging_message
async def report_command(message: Message, config: Config):
    """
    Хендлер для команды !report или /report.
    Позволяет пользователям пожаловаться на сообщение в чате.
    Следует писать только в ответ на сообщение, о котором необходимо сообщить.

    Handler for commands !report and /report.
    Command can be used for reporting to admins.
    You should write this command in response to a message you to report.
    """

    logger.info(
        "User {user} report message {message} in chat {chat} from user {from_user}".format(
            user=message.from_user.id,
            message=message.message_id,
            chat=message.chat.id,
            from_user=message.reply_to_message.from_user.id,
        ))
    # если группа частная, то формируем ссылку для перехода к группе,
    # а если публичная, то к ссылке на группу добавляем ссылку на сообщение для перехода к конкретному сообщению
    url_to_alert: str = await message.chat.get_url()
    if message.chat.username:
        url_to_alert: str = '/'.join([url_to_alert, f'{message.reply_to_message.message_id}'])

    chat_label: str = hlink(message.chat.title, url_to_alert)
    text = "[ALERT] Пользователь {user} пожаловался на сообщение id: {msg_to_del} в чате {chat}.".format(
        user=message.from_user.get_mention(),
        msg_to_del=message.reply_to_message.message_id,
        chat=chat_label,

    )

    await send_alert_to_admins(message=message, text=text, config=config)
    await message.reply_to_message.reply("Сообщение было отправлено администраторам")


def register_report_command(dp: Dispatcher):
    dp.register_message_handler(report_command,
                                is_reply=True,
                                chat_type=chat_types(),
                                commands=['report'],
                                commands_prefix='!/',
                                state='*')
