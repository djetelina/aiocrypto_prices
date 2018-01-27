class CryptoPriceException(Exception):
    pass


class CurrencyNotFound(CryptoPriceException):
    pass


class UnfetchedInformation(CryptoPriceException):
    pass
