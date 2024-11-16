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

    if uiic.redis_check_user_id() and await uiic.is_chat_member():
        if int(call.data.split(':')[1]) == config.redis_worker.get_capcha_key(uiic.id_user()):
            await call.answer(text=f"{uiic.user_name()}"
                                   f" you are pass!", show_alert=True)
            await call.bot.restrict_chat_member(chat_id=uiic.chat_id(), user_id=uiic.id_user(),
                                                permissions=ChatPermissions(can_send_messages=True),
                                                until_date=timedelta(seconds=config.time_delta.minute_delta))
            await call.bot.delete_message(chat_id=uiic.chat_id(), message_id=call.message.message_id)
            logger.info(f"User id:{uiic.id_user()} name:{uiic.user_name()}was pass")
            config.redis_worker.add_capcha_flag(uiic.id_user(), 1)
            greeting: str = greeting_text(call=call, bot_user=await call.message.bot.get_me())
            msg: Message = await call.message.answer(text=greeting, disable_web_page_preview=True,
                                                     reply_markup=ReplyKeyboardRemove())
            logger.info(f"New User id:{uiic.id_user()} name:{uiic.user_name()} was greeting")
            await asyncio.sleep(config.time_delta.time_rise_asyncio_del_msg)
            await msg.delete()
            logger.info(f"del greeting msg for {uiic.id_user()}")

        else:
            await call.message.bot.kick_chat_member(chat_id=uiic.chat_id(), user_id=uiic.id_user(),
                                                    until_date=timedelta(seconds=config.time_delta.minute_delta))
            await call.message.bot.unban_chat_member(chat_id=uiic.chat_id(), user_id=uiic.id_user())
            logger.info(f"User id:{uiic.id_user()} name:{uiic.user_name()} was kik")

    elif not await uiic.is_admin():
        await call.answer(text="don't be jerk!\n"
                               "sit in the corner 4 min", show_alert=True)
        await call.message.bot.restrict_chat_member(chat_id=uiic.chat_id(), user_id=uiic.id_user(),
                                                    permissions=ChatPermissions(can_send_messages=False),
                                                    until_date=timedelta(seconds=config.time_delta.minute_delta * 4))
        logger.info(f"User id:{uiic.id_user()} name:{uiic.user_name()} was mute seconds ="
                    f" {config.time_delta.minute_delta * 4}")
