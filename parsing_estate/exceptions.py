class NumberInLocationError(Exception):
    """Вызывается если пользователь указал в локации цифры"""

    pass


class LatinLettersLocationError(Exception):
    """Вызывается если пользователь указал в локации латинские буквы"""

    pass


class PunctuationCharError(Exception):
    """Вызывается если пользователь указал какие-то символы в локации"""

    pass


class UncorrectTimeCreateAd(Exception):
    """Вызывается если пользователь указал неверный формат для временной дельты"""

    pass


class ImportantConfigsDoNotExists(KeyError):
    """Вызывается когда пользователь не указал обязательные конфиги для парсера"""

    pass


class UnConnectedError(Exception):
    """ Вызывается когда по каким-то причинам происходит разрыв соединения"""