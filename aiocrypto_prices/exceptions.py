class CryptoPriceException(Exception):
    pass


class CurrencyNotFound(CryptoPriceException):
    pass
