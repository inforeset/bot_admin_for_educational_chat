from aiogram import Dispatcher
from aiogram.types import ChatType, Message

from tgbot.keyboards.reply.for_private import main_keyboard
from tgbot.utils.decorators import logging_message
from tgbot.utils.texts import user_commands_guide, user_help_text


@logging_message
async def echo_for_private(message: Message):
    """
    Эхо-хендлер на команды для ЛС с ботом. На команды высылает инфо-сообщение о недоступности использования команд в ЛС.
    """
    await message.reply('Все мои команды доступны только для групп. '
                        '\n\nЧтобы получить дополнительную информацию, нажмите на нужную кнопку ниже.',
                        reply_markup=main_keyboard())


@logging_message
async def send_info(message: Message) -> None:
    """
    Хендлер на сообщения для ЛС с ботом. На выбор с reply-клавиатуры выдает соответсвующую информацию,
    на остальные сообщения просит нажать на одну из кнопок в меню reply-клавиатуры
    """
    text = ''
    if message.text == 'Команды для чата: инструкция':
        text: str = user_commands_guide()
    elif message.text == 'Полезные ссылки для написания бота':
        text = user_help_text(message=message)

    if text:
        await message.answer(text,
                             disable_web_page_preview=True,
                             reply_markup=main_keyboard())
    else:
        await message.answer('Чтобы я вас верно понял, нажмите на кнопку в меню.',
                             reply_markup=main_keyboard())


def register_echo(dp: Dispatcher):
    dp.register_message_handler(echo_for_private,
                                chat_type=ChatType.PRIVATE,
                                commands=['help', 'report', 'paste'],
                                commands_prefix='/!',
                                state='*')

    dp.register_message_handler(send_info,
                                chat_type=ChatType.PRIVATE,
                                state='*')
