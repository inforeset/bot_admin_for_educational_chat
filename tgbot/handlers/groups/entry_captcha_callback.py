
from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from tgbot.utils.decorators import logging_message
from tgbot.config import Config
from tgbot.utils.capcha_check import check_captcha


@logging_message
async def captcha_answer(call: CallbackQuery, config: Config) -> None:
    """handler for inline captcha answer button
           param call: CallbackQuery
           return None
    """
    await check_captcha(call=call, config=config)


def register_callback_captcha(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(captcha_answer,
                                       lambda call: call.data.startswith("answer_button"))