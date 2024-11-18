import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import AllowedUpdates
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from tgbot.config import load_config
from tgbot.database.models import Base
from tgbot.database.utils import make_connection_string
from tgbot.filters.admin import AdminFilter
from tgbot.filters.custom_text import ThankMessageFilter

from tgbot.handlers.admin.admin import register_admin
from tgbot.handlers.admin.ban_to_user import register_bun
from tgbot.handlers.admin.ro_to_user import register_ro
from tgbot.handlers.for_incorrect_using_commands import register_incorrect_using_command
from tgbot.handlers.for_private.for_private import register_echo
from tgbot.handlers.groups.entry_captcha_callback import register_callback_captcha
from tgbot.handlers.groups.hastebin import register_paste_command
from tgbot.handlers.groups.report import register_report_command
from tgbot.handlers.groups.reputation import register_thank_message, register_reputation_command
from tgbot.handlers.groups.user import register_user
from tgbot.handlers.groups.new_member_info import register_new_member_info
from tgbot.handlers.groups.help_command import register_help_command
from tgbot.middlewares.check_groups import VerifiedGroupsMiddleware
from tgbot.middlewares.db import DbSessionMiddleware
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.utils.log_config import logger


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(VerifiedGroupsMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_echo(dp)
    register_incorrect_using_command(dp)
    register_callback_captcha(dp)

    register_bun(dp)
    register_ro(dp)

    register_help_command(dp)
    register_new_member_info(dp)
    register_paste_command(dp)
    register_report_command(dp)

    register_thank_message(dp)
    register_reputation_command(dp)


async def main():
    logger.info("Starting bot")
    config = load_config(".env")

    # Creating DB engine for PostgreSQL
    engine = create_async_engine(make_connection_string(config=config), future=True, echo=False)

    # Creating DB connections pool
    db_pool = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    bot['config'] = config

    dp.filters_factory.bind(ThankMessageFilter, event_handlers=[dp.message_handlers])

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)

    # Register middlewares
    dp.middleware.setup(DbSessionMiddleware(db_pool))

    try:
        config.redis_worker.del_all_key()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            allowed_updates=(
                    AllowedUpdates.CHAT_MEMBER
                    | AllowedUpdates.CALLBACK_QUERY
                    | AllowedUpdates.MESSAGE
                    | AllowedUpdates.EDITED_MESSAGE
            )
        )
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")