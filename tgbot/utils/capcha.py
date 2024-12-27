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

operators: dict = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
}

words_list = ['S', 'K', 'I', 'L', 'B', 'X', 'С', 'К', 'И', 'Л', 'Б']


def eval_binary_expr(variable_x, variable_y, math_operation) -> int:
    return operators[math_operation](int(variable_x), int(variable_y))


def gen_math_expression() -> dict:
    x: int = random.randint(1, 10)
    y: int = random.randint(10, x)
    random_operator: str = random.choice(list(operators.keys()))
    word_one: str = random.choice(words_list)
    word_two: str = random.choice(words_list)
    random_operator_two: str = random.choice(list(operators.keys()))
    random_operator_three: str = random.choice(list(operators.keys()))

    eval_string: str = "{} {} {} {} {} {} {}".format(
        x, random_operator, y, random_operator_two, word_one, random_operator_three, word_two
    )
    return {"expression": eval_string.format(x, random_operator, y) + " = ?",
            "answer": int(eval_binary_expr(x, y, random_operator))}


def gen_captcha(temp_capcha: str) -> BytesIO:
    """
     Take some int, generate object ImageCaptcha -> BytesIO return object BytesIO
    param temp_integer: int
    return: BytesIO
    """
    image: ImageCaptcha = ImageCaptcha(width=600, height=150)
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
    if uiic.is_new_user() and not await uiic.redis_flag():
        capcha_key: dict = gen_math_expression()
        await config.redis_worker.add_capcha_flag(uiic.id_user(), 0)
        await config.redis_worker.add_capcha_key(uiic.id_user(), capcha_key.get("answer"))
        captcha_image: InputFile = InputFile(gen_captcha(capcha_key.get("expression")))
        await message.bot.restrict_chat_member(chat_id=uiic.chat_id(), user_id=uiic.id_user(),
                                               permissions=ChatPermissions(can_send_messages=False),
                                               until_date=timedelta(seconds=config.time_delta.time_rise_asyncio_ban))
        logger.info(f"User {uiic.id_user()} mute before answer")
        caption: str = (f"Привет, {uiic.user_name()}! Для начала решите капчу. "
                        f"\nНадо посчитать только цифры, буквы в расчет не брать! "
                        f"\nПожалуйста ответьте, иначе Вас кикнут!")
        msg: Message = await message.bot.send_photo(chat_id=uiic.chat_id(),
                                                    photo=captcha_image,
                                                    caption=caption,
                                                    reply_markup=gen_captcha_button_builder(
                                                        capcha_key.get("answer"))
                                                    )
        logger.info(f"User {uiic.id_user()} throw captcha")

        # FIXME change to schedule (use crone, scheduler, nats..)
        await asyncio.sleep(config.time_delta.time_rise_asyncio_ban)
        try:
            await msg.delete()
            logger.info(f"for User {uiic.id_user()} del msg captcha")
        except MessageToDeleteNotFound as error:
            logger.info(f"{error} msg {uiic.id_user()}")
        try:
            if await config.redis_worker.get_capcha_flag(uiic.id_user()) == 1:
                await config.redis_worker.del_capcha_flag(uiic.id_user())
                await config.redis_worker.del_capcha_key(uiic.id_user())
                logger.info(f"for User {uiic.id_user()} pass\n del capcha key, flag")
            else:
                await message.bot.kick_chat_member(chat_id=uiic.chat_id(), user_id=uiic.id_user(),
                                                   until_date=timedelta(seconds=config.time_delta.minute_delta))
                await message.bot.unban_chat_member(chat_id=uiic.chat_id(), user_id=uiic.id_user())
                logger.info(f"User {uiic.id_user()} was kicked ")
                await config.redis_worker.del_capcha_flag(uiic.id_user())
                await config.redis_worker.del_capcha_key(uiic.id_user())
                logger.info(f"for User {uiic.id_user()} no pass\n del capcha key, flag")
        except TypeError as err:
            logger.info(f"for User {uiic.id_user()} not have captcha flag")

    else:
        pass


if __name__ == '__main__':
    pass
