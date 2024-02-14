import asyncio

from aiogram.types import ChatPermissions, CallbackQuery, Message, ReplyKeyboardRemove, User
from datetime import timedelta

from typing import List

from tgbot.utils.texts import greeting_text
from tgbot.utils.log_config import logger
from tgbot.utils.admin_ids import get_admins_ids_for_help_and_paste
from tgbot.config import Config


async def check_captcha(call: CallbackQuery, config: Config):
    """
        func check pass rise ban or mute
               param call: CallbackQuery
               return None
        """
    # FIXME 2) optimise ternary too OOP
    admin_ids: List[int] = await get_admins_ids_for_help_and_paste(call.message)
    capcha_key: int = int(call.data.split(':')[1])
    user_id: int = int(call.from_user.id)
    chat_id: int = int(call.message.chat.id)
    minute_delta: int = config.time_delta.minute_delta
    list_users_redis: list[int] = list(map(int, config.redis_worker.get_all_capcha_user_key()))
    if call.message.chat.get_member(user_id):
        if user_id in admin_ids:
            msg_temp = await call.message.answer(text="Админ не балуйся \n"
                                                      "иди работать!")
            await asyncio.sleep(minute_delta)
            try:
                await msg_temp.delete()
            except AttributeError as error:
                logger.info(f"user id {user_id}  {error}")

            logger.info(f"admin:{user_id} name:{call.from_user.full_name} was play")
        else:
            if user_id in list_users_redis:
                if capcha_key == config.redis_worker.get_capcha_key(user_id):
                    await call.answer(text=f"{call.from_user.full_name}"
                                           f" you are pass!", show_alert=True)
                    await call.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id,
                                                        permissions=ChatPermissions(can_send_messages=True),
                                                        until_date=timedelta(seconds=minute_delta))
                    await call.bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
                    logger.info(f"User id:{user_id} name:{call.from_user.full_name}was pass")
                    config.redis_worker.add_capcha_flag(user_id, 1)
                    bot_user: User = await call.message.bot.get_me()
                    greeting: str = greeting_text(call=call, bot_user=bot_user)
                    msg: Message = await call.message.answer(text=greeting, disable_web_page_preview=True,
                                                             reply_markup=ReplyKeyboardRemove())
                    logger.info(f"New User id:{user_id} name:{call.from_user.full_name} was greeting")
                    await asyncio.sleep(config.time_delta.time_rise_asyncio_del_msg)
                    await msg.delete()
                    logger.info(f"del greeting msg for {user_id}")

                else:
                    await call.message.bot.kick_chat_member(chat_id=chat_id, user_id=user_id,
                                                            until_date=timedelta(seconds=minute_delta))
                    await call.message.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
                    logger.info(f"User id:{user_id} name:{call.from_user.full_name} was kik")

            else:
                await call.answer(text="don't be jerk!\n"
                                       "sit in the corner 4 min", show_alert=True)
                await call.message.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id,
                                                            permissions=ChatPermissions(can_send_messages=False),
                                                            until_date=timedelta(seconds=minute_delta * 4))
                logger.info(f"User id:{user_id} name:{call.from_user.full_name} was mute seconds = {minute_delta * 4}")
