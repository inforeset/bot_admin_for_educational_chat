from io import BytesIO
from captcha.image import ImageCaptcha

import random
import asyncio
from datetime import timedelta

from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.types import Message, InputFile, ChatPermissions, ChatMemberUpdated

from tgbot.keyboards.Inline.captcha_keys import gen_captcha_button_builder
from tgbot.utils.log_config import logger
from tgbot.utils.decorators import logging_message
from tgbot.config import Config
import operator
from tgbot.utils.worker_user import UserIdentificationInChat
# TODO replace method kik(deprecated) on ban, splas capha files

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
    eval_string: str = " {} {} {}"
    return {"expression": eval_string.format(x, random_operator, y) + " = ?",
            "answer": int(eval_binary_expr(x, y, random_operator))}


def gen_captcha(temp_capcha: str) -> BytesIO:
    """
     Take some int, generate object ImageCaptcha -> BytesIO return object BytesIO
    param temp_integer: int
    return: BytesIO
    """
    image: ImageCaptcha = ImageCaptcha()
    data: BytesIO = image.generate(temp_capcha)
    return data


@logging_message
async def throw_capcha(message: ChatMemberUpdated, config: Config) -> None:
    """
           generate captcha image send to user in chat
           param message: Message
           return None
    """

    uiic: UserIdentificationInChat = UserIdentificationInChat(obj=message, config=config)
    if uiic.is_new_user():
        user_id: int = uiic.id_user()
        chat_id: int = int(message.chat.id)
        capcha_key: dict = gen_math_expression()
        config.redis_worker.add_capcha_key(user_id, capcha_key.get("answer"))
        captcha_image: InputFile = InputFile(gen_captcha(capcha_key.get("expression")))
        await message.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id,
                                               permissions=ChatPermissions(can_send_messages=False),
                                               until_date=timedelta(seconds=config.time_delta.time_rise_asyncio_ban))
        logger.info(f"User {user_id} mute before answer")
        caption: str = f'Привет, {uiic.user_name()} пожалуйста ответьте иначе Вас кикнут!'
        msg: Message = await message.bot.send_photo(chat_id=chat_id,
                                                    photo=captcha_image,
                                                    caption=caption,
                                                    reply_markup=gen_captcha_button_builder(
                                                        capcha_key.get("answer"))
                                                    )
        logger.info(f"User {user_id} throw captcha")

        # FIXME change to schedule (use crone, scheduler, nats..)
        await asyncio.sleep(config.time_delta.time_rise_asyncio_ban)
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
                                                   until_date=timedelta(seconds=config.time_delta.minute_delta))
                await message.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
                logger.info(f"User {user_id} was kicked = {config.time_delta.minute_delta}")
                config.redis_worker.del_capcha_flag(user_id)
                config.redis_worker.del_capcha_key(user_id)
                logger.info(f"for User {user_id} no pass\n del capcha key, flag")
        except TypeError as err:
            logger.info(f"for User {user_id} not have captcha flag")

    else:
        pass


if __name__ == '__main__':
    pass
