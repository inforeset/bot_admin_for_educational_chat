from aiogram.types import (
    CallbackQuery, Message, ChatMember, User,
    ChatMemberLeft, ChatMemberBanned
)
from tgbot.utils.admin_ids import get_admins_ids_for_help_and_paste
from typing import List
from tgbot.config import Config



class UserIdentificationInChat:
    """
    A helper class to determine a user from a CallbackQuery or Message.
    """

    def __init__(self, obj: Message | CallbackQuery, config: Config):
        self.obj: Message | CallbackQuery = obj
        self.config: Config = config

    def is_callback(self) -> bool:
        """
        Determines the type of object being used.
        """
        return isinstance(self.obj, CallbackQuery)

    def chat_id(self) -> int:
        if self.is_callback():
            return int(self.obj.message.chat.id)
        else:
            return int(self.obj.chat.id)

    def id_user(self) -> int:
        if self.is_new_user():
            if self.is_callback():
                return int(self.obj.message.new_chat_member.id)
            else:
                return int(self.obj.new_chat_member.user.id)
        else:
            return int(self.obj.from_user.id)

    def user_name(self) -> str:
        if self.is_new_user():
            return self.obj.new_chat_member.user.full_name
        else:
            if self.is_callback():
                return self.obj.message.from_user.full_name
            else:
                return self.obj.from_user.full_name

    def is_new_user(self) -> bool:
        """Checks if the user is new."""
        if self.is_callback():
            try:
                new_users: List[User] = self.obj.message.new_chat_member
                return True
            except AttributeError:
                return False
        else:
            try:
                new_users: List[User] = self.obj.new_chat_member
                return True
            except AttributeError:
                return False

    async def is_chat_member(self) -> bool:
        """
        Checks if the user is a member of the chat.
        """
        chat_member = await self.obj.bot.get_chat_member(chat_id=self.chat_id(), user_id=self.id_user())
        return not isinstance(chat_member, (ChatMemberLeft, ChatMemberBanned))

    async def is_admin(self) -> bool:
        """
        Checks if the user is an admin of the chat.
        """
        user_id: int = self.id_user()

        if self.is_callback():
            admins: List[int] = await get_admins_ids_for_help_and_paste(self.obj.message)
        else:
            admins: List[ChatMember] = await self.obj.bot.get_chat_administrators(self.obj.chat.id)
            admins = [admin.user.id for admin in admins]  # Extract admin IDs.

        return user_id in admins

    async def redis_check_user_id(self) -> bool:
        """
        Checks if the user's ID exists in Redis captcha keys.
        """
        user_id = self.id_user()
        captcha_keys = await self.config.redis_worker.get_all_capcha_user_key()
        return int(user_id) in list(map(int, captcha_keys))

    async def redis_flag(self) -> bool:
        """
        Checks if the user's flag exists in Redis.
        """
        try:
            flag = await self.config.redis_worker.get_capcha_flag(self.id_user())
            return flag is not None
        except TypeError:
            return False
