import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import AllowedUpdates

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin.admin import register_admin
from tgbot.handlers.admin.ban_to_user import register_bun_to_user
from tgbot.handlers.admin.ro_to_user import register_ro
from tgbot.handlers.admin.set_readonly_to_user import register_set_readonly_to_user
from tgbot.handlers.groups.user import register_user
from tgbot.handlers.groups.new_member_info import register_new_member_info
from tgbot.handlers.groups.help_command import register_help_command
from tgbot.middlewares.environment import EnvironmentMiddleware

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_bun_to_user(dp)
    register_ro(dp)
    register_set_readonly_to_user(dp)

    register_user(dp)
    register_help_command(dp)
    register_new_member_info(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            allowed_updates=AllowedUpdates.MESSAGE +
                            AllowedUpdates.CHAT_MEMBER +
                            AllowedUpdates.CALLBACK_QUERY +
                            AllowedUpdates.EDITED_MESSAGE)
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
