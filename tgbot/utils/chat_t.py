from aiogram.types import ChatType


def chat_types() -> list[ChatType]:
    """ Функция, возвращающая список доступных типов групп для фильтрации сообщений в хендлере

    :return: GROUP и SUPERGROUP
    """
    return [ChatType.GROUP, ChatType.SUPERGROUP]
