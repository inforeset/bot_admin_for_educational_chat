import datetime
import re

from aiogram import types


PATTERN = re.compile(r"(?P<value>\d+)(?P<modifier>[wdhms])")
LINE_PATTERN = re.compile(r"^(\d+[wdhms]){1,}$")

MODIFIERS = {
    "w": datetime.timedelta(weeks=1),
    "d": datetime.timedelta(days=1),
    "h": datetime.timedelta(hours=1),
    "m": datetime.timedelta(minutes=1),
    "s": datetime.timedelta(seconds=1),
}


class TimedeltaParseError(Exception):
    pass


def parse_timedelta(value: str) -> datetime.timedelta:
    """ Функция для проверки передаваемого аргумента на соответствие паттерну и дальнейшего преобразования
     аргумента к типу timedelta.

     :param value: аргументы команды !ro
     :return: объект типа timedelta (если команда была передана без аргументов, то назначается 15 минут по умолчанию)
     """

    match = LINE_PATTERN.match(value)
    if not match:
        raise TimedeltaParseError("Invalid time format")

    try:
        result = datetime.timedelta()
        for match in PATTERN.finditer(value):
            value, modifier = match.groups()
            result += int(value) * MODIFIERS[modifier]

    except OverflowError:
        raise TimedeltaParseError("Timedelta value is too large")

    return result


async def parse_timedelta_from_message(message: types.Message) -> datetime.timedelta:
    """ Функция, которая возвращает конкретное значение типа timedelta для обработки команды !ro

    :param message: объект сообщения от пользователя;
    :return: объект типа timedelta
    """

    _, *args = message.text.split()

    # если аргументов к команде нет, то возвращаем значение по умолчанию (15 минут)
    if not args:
        return datetime.timedelta(minutes=15)

    try:
        duration: datetime.timedelta = parse_timedelta(args[0])
        if duration <= datetime.timedelta(minutes=1):
            return datetime.timedelta(minutes=1)
        return duration

    except TimedeltaParseError:
        await message.reply("Аргументы команды <i>!ro</i> указаны неверно")