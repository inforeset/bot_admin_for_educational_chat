from aiogram.types import Message, User, Chat, CallbackQuery

from tgbot.utils.log_config import logger


async def add_to_log_message(message) -> None:
    """
        Добавляет в лог информацию о сообщении
        Add info (Message or CallbackQuery)  to log
        param message: Message or CallbackQuery
        return None

    """
    if isinstance(message, Message):
        user_info: str = await get_user_info(message.from_user)
        chat: Chat = message.chat
        log_text: str = f'get message from user[{user_info}] in chat: [ID:{chat.id};name:{chat.full_name}]' \
                        f'\nmsg: [ID:{message.message_id};text: {message.text}]'
        if message.reply_to_message:
            reply_user_info = await get_user_info(message.reply_to_message.from_user)
            log_text += f'\nreply to msg: [ID:{message.reply_to_message.message_id};' \
                        f'text: {message.reply_to_message.text}] ' \
                        f'\nfrom user [{reply_user_info}]'
        logger.info(log_text)
    elif isinstance(message, CallbackQuery):
        user_info: str = await get_user_info(message.from_user)
        chat = message.message.chat
        log_text: str = f'get message from user[{user_info}] in chat: [ID:{chat.id};name:{chat.full_name}]' \
                        f'\nmsg: [ID:{message.message.message_id};data: {message.data}]'
        logger.info(log_text)


async def get_user_info(user: User) -> str:
    """
    Возвращает строку с данными пользователя
    """

    user_list = [f'ID:{user.id}']
    if user.username:
        user_list.append(f'@{user.username}')
    user_list.append(f'name: {user.username}')
    return ';'.join(user_list)