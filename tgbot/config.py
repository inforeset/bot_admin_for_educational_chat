from dataclasses import dataclass

from environs import Env
from tgbot.utils.worker_redis import WorkerRedis


@dataclass
class TimingDelta:
    time_rise_asyncio_ban: int
    minute_delta: int
    time_rise_asyncio_del_msg: int


@dataclass
class TgBot:
    token: str
    send_report_to_owner: bool


@dataclass
class Miscellaneous:
    hastebin_url: str
    verified_groups: list[int]


@dataclass
class Database:
    host: str
    user: str
    name: str
    port: str
    password: str


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous
    db: Database
    time_delta: TimingDelta
    redis_worker: WorkerRedis


def load_config(path: str = None):
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            send_report_to_owner=env.bool("SEND_REPORT_TO_OWNER"),
        ),
        misc=Miscellaneous(
            hastebin_url=env.str("HASTEBIN_URL"),
            verified_groups=list(map(int, env.list("VERIFIED_GROUPS")))
        ),
        db=Database(
            host=env.str("POSTGRES_HOST"),
            user=env.str("POSTGRES_USER"),
            name=env.str("POSTGRES_DB"),
            port=env.str("POSTGRES_PORT"),
            password=env.str("POSTGRES_PASSWORD"),
        ),
        time_delta=TimingDelta(
            time_rise_asyncio_ban=int(env.str("TIME_RAISE_ASYNCIO_BAN")),
            minute_delta=int(env.str("TIME_ONE_MINUTE")),
            time_rise_asyncio_del_msg=int(env.str("TIME_RAISE_ASYNCIO_DEL_MSG")),
        ),
        redis_worker=WorkerRedis(redis_container_name=env.str("REDIS_CONTAINER_NAME"),
                                 redis_host_name=env.str("REDIS_HOST_NAME"),
                                 redis_port=int(env.str("REDIS_HOST_PORT")), )
    )