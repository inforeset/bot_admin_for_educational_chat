from aiogram.types import Message, ChatMember


from tgbot.config import Config


async def get_admins_ids_for_report(message: Message, config: Config) -> list[int]:
    """
    Возвращает id админов группы, с id владельца или без него,
    зависит от параметра send_report_to_owner
    """
    send_report_to_owner: bool = config.tg_bot.send_report_to_owner
    admins: list[int] = await get_admins_ids_for_help_and_paste(message)
    owner: int = await _get_owner_id(message)
    if not send_report_to_owner:
        admins.remove(owner)

    return admins


async def get_admins_ids_for_help_and_paste(message: Message) -> list[int]:
    """
    Возвращает id админов группы, включая владельца группы
    """
    admins: list = await _get_all_admins(message)

    return [
        admin.user.id
        for admin in admins
        if not admin.user.is_bot
    ]


async def _get_owner_id(message) -> int:
    """ Возвращает id владельца группы """

    admins: list[ChatMember] = await _get_all_admins(message)
    return [
            admin.user.id
            for admin in admins
            if admin.is_chat_owner()
        ][0]


async def _get_all_admins(message: Message) -> list[ChatMember]:
    """ Возвращает список всех не ботов администраторов группы """

    admins: list[ChatMember] = await message.bot.get_chat_administrators(message.chat.id)

    return [
        admin
        for admin in admins
        if not admin.user.is_bot
    ]
