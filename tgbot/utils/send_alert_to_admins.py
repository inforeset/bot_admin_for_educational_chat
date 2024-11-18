import asyncio
from contextlib import suppress

from aiogram.types import Message
from aiogram.utils.exceptions import Unauthorized, MessageToDeleteNotFound

from tgbot.config import Config
from tgbot.utils.admin_ids import get_admins_ids_for_report
from tgbot.utils.log_config import logger


async def send_alert_to_admins(message: Message, text: str, config: Config) -> None:
    """ Функция для отправки уведомлений администраторам по командам ban, ro и report """

    admin_ids: list = await get_admins_ids_for_report(message=message, config=config)

    with suppress(MessageToDeleteNotFound):
        await message.delete()
        logger.info("Report message deleted: {message_id}".format(message_id=message.message_id))

    for admin_id in admin_ids:
        with suppress(Unauthorized):
            await message.bot.send_message(admin_id, text)
            logger.info("Send alert message to admin {admin}".format(admin=admin_id))
            await asyncio.sleep(0.3)
