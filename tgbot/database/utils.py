from tgbot.config import Config


def make_connection_string(config: Config) -> str:
    """
    Make connection string to db
    """
    return (
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@"
        f"{config.db.host}:{config.db.port}/{config.db.name}"
    )
