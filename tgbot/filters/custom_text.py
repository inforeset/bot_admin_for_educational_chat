from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class ThankMessageFilter(BoundFilter):
    """
    Checking for the number of characters in a message/callback_data
    """

    key = "custom_text"

    def __init__(self, custom_text: Union[str, list[str]]):
        if isinstance(custom_text, str):
            self.custom_text = [custom_text]

        elif isinstance(custom_text, list):
            self.custom_text = custom_text
        else:
            raise ValueError(
                f"filter letters must be a int, not {type(custom_text).__name__}"
            )

    # FIXME  obj is NoneType
    async def check(self, obj: Union[types.Message, types.Sticker]):
        data = obj.text or obj.sticker.emoji if obj.sticker else obj.text
        if data:
            if any(word in data.lower() for word in self.custom_text):
                return True
        return False