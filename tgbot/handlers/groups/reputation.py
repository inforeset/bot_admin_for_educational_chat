import asyncio
from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from sqlalchemy import select, desc

from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.database.models import Reputation
from tgbot.utils.chat_t import chat_types
from tgbot.utils.decorators import logging_message


@logging_message
async def thank_message(message: types.Message, session: AsyncSession) -> None:
    """
    Хендлер для поднятия репутации.


    :param message: объект сообщения от пользователя;
    :param session: объект асинхронной сессии алхимии
    """

    query = await session.execute(
        select(
            Reputation
        ).where(
            Reputation.user_id == message.reply_to_message.from_user.id
        )
    )

    reputation = query.scalars().first()

    if not reputation:
        reputation = Reputation()
        reputation.user_id = message.reply_to_message.from_user.id
        reputation.scores = 1
        reputation.link = message.reply_to_message.from_user.get_mention(as_html=True)
    else:
        reputation.scores = Reputation.scores + 1

    session.add(reputation)
    await session.commit()
    await session.refresh(reputation)

    msg_to_delete_in_30sec = await message.reply_to_message.reply(
        f"{message.reply_to_message.from_user.get_mention(as_html=True)}, {message.from_user.get_mention(as_html=True)}"
        f" повысил(а) вашу репутацию.\nВаша репутация {reputation.scores}."
    )

    await asyncio.sleep(30)
    with suppress(TelegramAPIError):
        await msg_to_delete_in_30sec.delete()


def register_thank_message(dp: Dispatcher):
    check_list = [
        "спасибо",
        "спс",
        "благодарю",
        "👍",
        "thanks",
        "thank you",
        "thank"
    ]

    dp.register_message_handler(
        thank_message,
        is_reply=True,
        chat_type=chat_types(),
        custom_text=check_list,
        state='*',
        content_types='any'
    )


@logging_message
async def reputation_command(message: types.Message, session: AsyncSession) -> None:
    """
    Хендлер для возврата по команде списка юзеров с очками репутации.


    :param message: объект сообщения от пользователя;
    :param session: объект асинхронной сессии алхимии
    """

    query = await session.execute(
        select(
            Reputation
        ).order_by(
            desc(Reputation.scores)
        )
    )

    reputations = query.scalars().all()

    msg = ""
    for reputation in reputations:
        msg += f"<code>{reputation.scores}</code> {reputation.link}\n"
    if not reputations:
        msg = "Еще нет участников с очками репутации"

    msg_to_delete_in_30sec = await message.answer(
        msg
    )

    await asyncio.sleep(30)
    with suppress(TelegramAPIError):
        await msg_to_delete_in_30sec.delete()


def register_reputation_command(dp: Dispatcher):
    dp.register_message_handler(
        reputation_command,
        is_reply=False,
        chat_type=chat_types(),
        commands=["toprep"],
        commands_prefix='!/',
        state='*',
    )