import asyncio

from aiogram.types import ChatPermissions, CallbackQuery, Message, ReplyKeyboardRemove
from datetime import timedelta

from tgbot.utils.texts import greeting_text
from tgbot.utils.log_config import logger
from tgbot.config import Config
from tgbot.utils.worker_user import UserIdentificationInChat


async def check_captcha(call: CallbackQuery, config: Config):
    """
        func check pass rise ban or mute
               param call: CallbackQuery
               return None
        """
    uiic: UserIdentificationInChat = UserIdentificationInChat(obj=call, config=config)
    user_id = uiic.id_user()
    user_name = uiic.user_name()
    chat_id = uiic.chat_id()
    if await uiic.redis_check_user_id() and await uiic.is_chat_member():
        if  int(call.data.split(':')[1]) == await config.redis_worker.get_capcha_key(user_id):
            await call.answer(text=f"{user_name}"
                                   f" you are pass!", show_alert=True)
            await call.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id,
                                                permissions=ChatPermissions(can_send_messages=True),
                                                until_date=timedelta(seconds=config.time_delta.minute_delta))
            await call.bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
            logger.info(f"User id:{user_id} name:{user_name} was pass")
            await config.redis_worker.add_capcha_flag(user_id, 1)
            greeting: str = greeting_text(call=call, bot_user=await call.message.bot.get_me())
            msg: Message = await call.message.answer(text=greeting, disable_web_page_preview=True,
                                                     reply_markup=ReplyKeyboardRemove())
            logger.info(f"New User id:{user_id} name: {user_name} was greeting")
            await asyncio.sleep(config.time_delta.time_rise_asyncio_del_msg)
            await msg.delete()
            logger.info(f"del greeting msg for {user_id}")

        else:
            await call.message.bot.kick_chat_member(chat_id=chat_id, user_id=user_id,
                                                    until_date=timedelta(seconds=config.time_delta.minute_delta))
            await call.message.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
            logger.info(f"User id:{user_id} name:{user_name} was kik")

    elif not await uiic.is_admin():
        await call.answer(text="don't be jerk!\n"
                               "sit in the corner 4 min", show_alert=True)
        await call.message.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id,
                                                    permissions=ChatPermissions(can_send_messages=False),
                                                    until_date=timedelta(seconds=config.time_delta.minute_delta * 4))
        logger.info(f"User id:{user_id} name:{user_name} was mute seconds ="
                    f" {config.time_delta.minute_delta * 4}")
