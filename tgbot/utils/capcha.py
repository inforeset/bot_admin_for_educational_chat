from io import BytesIO
from captcha.image import ImageCaptcha

import random
import asyncio
from datetime import timedelta

from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.types import Message, InputFile, ChatPermissions, ChatMemberUpdated, ReplyKeyboardRemove, ChatMember
from typing import List

from tgbot.keyboards.Inline.captcha_keys import gen_captcha_button_builder
from tgbot.utils.log_config import logger
from tgbot.utils.decorators import logging_message
from tgbot.config import Config
import operator


operators: dict = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '%': operator.mod,
    '^': operator.xor,
}


def eval_binary_expr(variable_x, variable_y, math_operation) -> int:
    return operators[math_operation](int(variable_x), int(variable_y))


def gen_math_expression() -> dict:
    x: int = random.randint(1, 9)
    y: int = random.randint(1, 9)
    random_operator: str = random.choice(list(operators.keys()))
    eval_string: str = "{} {} {}"
    return {"expression": eval_string.format(x, random_operator, y) + "=?",
            "answer": int(eval_binary_expr(x, y, random_operator))}


def gen_captcha(temp_integer: int) -> BytesIO:
    """
     Take some int, generate object ImageCaptcha -> BytesIO return object BytesIO
    param temp_integer: int
    return: BytesIO
    """
    image: ImageCaptcha = ImageCaptcha()
    data: BytesIO = image.generate(str(temp_integer))
    return data


@logging_message
async def throw_capcha(message: ChatMemberUpdated, config: Config) -> None:
    """
           generate captcha image send to user in chat
           param message: Message
           return None
    """
    admins: List[ChatMember] = await message.bot.get_chat_administrators(message.chat.id)
    admin_ids: List[int] = [admin.user.id for admin in admins if not admin.user.is_bot]
    user_id: int = int(message.from_user.id)
    user_name: str = message.from_user.full_name
    chat_id: int = int(message.chat.id)
    time_rise_asyncio_ban: int = config.time_delta.time_rise_asyncio_ban
    minute_delta: int = config.time_delta.minute_delta
    try:
        new_user_id: int = int(message.new_chat_member.user.id)
        user_id = new_user_id
        user_name = message.new_chat_member.user.full_name
    except IndexError as err:
        logger.info(f"User {user_id} {user_name} not new {err}")
    if user_id in admin_ids:
        msg = await message.bot.send_message(chat_id=chat_id, disable_web_page_preview=True,
                                             text="Админ не балуйся иди работать!", reply_markup=ReplyKeyboardRemove())
        logger.info("New User {user} was greeting".format(
            user=message.new_chat_member.user.id)
        )
        await asyncio.sleep(minute_delta)
        await msg.delete()
        logger.info(f"admin:{user_id} name:{message.from_user.full_name} was play")
    else:
        capcha_key: dict = gen_math_expression()
        config.redis_worker.add_capcha_key(user_id, capcha_key.get("answer"))
        captcha_image: InputFile = InputFile(gen_captcha(capcha_key.get("expression")))
        await message.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id,
                                               permissions=ChatPermissions(can_send_messages=False),
                                               until_date=timedelta(seconds=time_rise_asyncio_ban))
        logger.info(f"User {user_id} mute before answer")
        caption: str = f'Привет, {user_name} пожалуйста ответьте иначе Вас кикнут!'
        msg: Message = await message.bot.send_photo(chat_id=chat_id,
                                                    photo=captcha_image,
                                                    caption=caption,
                                                    reply_markup=gen_captcha_button_builder(capcha_key.get("answer"))
                                                    )
        logger.info(f"User {user_id} throw captcha")
        # FIXME change to schedule (use crone, scheduler, nats..)
        await asyncio.sleep(time_rise_asyncio_ban)
        try:
            await msg.delete()
            logger.info(f"for User {user_id} del msg captcha")
        except MessageToDeleteNotFound as error:
            logger.info(f"{error} msg {user_id}")
        try:
            if config.redis_worker.get_capcha_flag(user_id) == 1:
                config.redis_worker.del_capcha_flag(user_id)
                config.redis_worker.del_capcha_key(user_id)
                logger.info(f"for User {user_id} pass\n del capcha key, flag")
            else:
                await message.bot.kick_chat_member(chat_id=chat_id, user_id=user_id,
                                                   until_date=timedelta(seconds=minute_delta))
                logger.info(f"User {user_id} was kicked = {minute_delta}")
                config.redis_worker.del_capcha_flag(user_id)
                config.redis_worker.del_capcha_key(user_id)
                logger.info(f"for User {user_id} no pass\n del capcha key, flag")
        except TypeError as err:
            logger.info(f"for User {user_id} not have captcha flag")


if __name__ == '__main__':
    pass
