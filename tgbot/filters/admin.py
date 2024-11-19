import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, ChatMemberOwner, ChatMemberAdministrator, ChatMember


class AdminFilter(BoundFilter):
    """ Класс для кастомного фильтра на хендлер сообщений для проверки на роль администратора """

    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    @staticmethod
    async def check(message: Message) -> bool:
        """ Метод класса AdminFilter для проверки на роль администратора группы

        :param message: объект сообщения от пользователя
        :returns: True или False
        """

        member: ChatMember = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if isinstance(member, ChatMemberOwner) or isinstance(member, ChatMemberAdministrator):
            return True
        return False
