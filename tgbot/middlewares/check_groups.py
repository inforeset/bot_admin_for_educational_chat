from aiogram import types
from aiogram.dispatcher.handler import current_handler, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import ChatType


class VerifiedGroupsMiddleware(BaseMiddleware):
    """
    Необрабатывать сообщения если получены из неразрешенных групп
    Cancel handler if get message from unverified group
    """

    def __init__(self):
        super(VerifiedGroupsMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        This handler is called when dispatcher receives a message
        :param data:
        :param message:
        """

        handler = current_handler.get()

        if not handler:
            return
        if message.chat.id not in data['config'].misc.verified_groups and message.chat.type != ChatType.PRIVATE:
            raise CancelHandler()