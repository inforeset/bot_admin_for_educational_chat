from aiogram.types import (CallbackQuery, Message, ChatMember, User,
                           ChatMemberLeft, ChatMemberBanned)
from tgbot.utils.admin_ids import get_admins_ids_for_help_and_paste
from typing import List
from tgbot.config import Config


class UserIdentificationInChat:
    """
        A helper class to determine a user from a CallbackQuery,Message

    """

    def __init__(self, obj: Message or CallbackQuery, config: Config):
        self.obj: Message or CallbackQuery = obj
        self.config: Config = config

    def is_callback(self) -> bool:
        """
        determines the type of object being use
        """
        if isinstance(self.obj, CallbackQuery):
            return True
        else:
            return False

    def chat_id(self) -> int:
        if self.is_callback():
            return int(self.obj.message.chat.id)
        else:
            return int(self.obj.chat.id)

    def id_user(self) -> int:
        if self.is_new_user():
            if self.is_callback():
                user_id: int = int(self.obj.message.new_chat_member.id)
            else:
                user_id: int = int(self.obj.new_chat_member.user.id)
            return int(user_id)
        else:
            if self.is_callback():
                user_id: int = int(self.obj.from_user.id)
            else:
                user_id: int = int(self.obj.from_user.id)
            return int(user_id)

    def user_name(self) -> str:
        if self.is_new_user():
            if self.is_callback():
                user_name: str = self.obj.new_chat_member.user.full_name
            else:
                user_name: str = self.obj.new_chat_member.user.full_name
            return user_name
        else:
            if self.is_callback():
                user_name: str = self.obj.message.from_user.full_name
            else:
                user_name: str = self.obj.from_user.full_name
            return user_name

    def is_new_user(self) -> bool:
        """in trow capcha check if user is new """
        if self.is_callback():
            try:
                new_users: List[User] = self.obj.message.new_chat_member
                return True
            except AttributeError as err:
                return False

        else:
            try:
                new_users: List[User] = self.obj.new_chat_member
                return True
            except AttributeError as err:
                return False

    async def is_chat_member(self) -> bool:
        if await self.obj.bot.get_chat_member(chat_id=self.chat_id(), user_id=self.id_user()) not in [ChatMemberLeft, ChatMemberBanned]:
            return True
        else:
            return False

    async def is_admin(self) -> bool:
        if self.is_callback():
            admins: List[int] = await get_admins_ids_for_help_and_paste(self.obj.message)

        else:
            admins: List[ChatMember] = await self.obj.bot.get_chat_administrators(self.obj.chat.id)
        user_id: int = self.id_user()
        return user_id in admins

    def redis_check_user_id(self) -> bool:
        if self.is_callback():
            return self.id_user() in list(map(int, self.config.redis_worker.get_all_capcha_user_key()))

    def redis_flag(self) -> bool:
        try:
            self.config.redis_worker.get_capcha_flag(self.id_user())
            return True
        except TypeError as err:
            return False
