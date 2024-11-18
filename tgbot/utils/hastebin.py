from urllib.parse import urljoin

from aiohttp import ClientSession


class HasteBinClient:
    """ Класс для формирования документа и уникальной ссылки на него на hastebin сервере """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def format_url(self, user_url: str) -> str:
        """ Метод класса HasteBinClient для форматирования базового URL-адреса hastebin сервера в уникальный URL-адрес,
        где будет расположен документ, который был отправлен на сервер.

        :param user_url: сформированная уникальная часть URL-адреса для пользователя, чей текст отправляется на сервер
        :return: полный URL-адрес для документа
        """
        return urljoin(self.base_url, user_url)

    async def create_document(self, content: bytes) -> dict[str, str]:
        """ Метод класса HasteBinClient для формирования уникальной части URL-адреса для конкретного документа,
        который будет размещен на hastebin сервере.

        :param content: закодированный текст
        :return: словарь, где по ключу "key" лежит сформированная уникальная часть URL-адреса для документа
        """
        async with ClientSession() as session:
            async with session.post(url=self.format_url("/documents"), data=content) as response:
                response.raise_for_status()
                result = await response.json()
                return result


def get_hastebin_client(url: str) -> HasteBinClient:
    """ Функция для передачи параметра url из файла конфигурации в конструктор экземпляра класса

    :param url: URL-адрес hastebin сервера
    :return: экземпляр класса HasteBinClient
    """
    return HasteBinClient(url)