from typing import List, Any, Dict, Union, Awaitable

import asyncio

import time

from aiocrypto_prices._api_requests import fetch_price_data, fetch_coin_list
from exceptions import CurrencyNotFound


class Prices:
    """Prices object"""
    def __init__(self, currency: 'Currency') -> None:
        self._prices: Dict[str, float] = {}
        self.currency = currency

    async def get(self, currency: str, default: Any=None) -> Any:
        """
        Gets the price for a specified currency, if currency is not in target currencies,
        it's added there for the specific currency
        """
        if currency not in self.currency.target_currencies:
            self.currency.target_currencies.append(currency.upper())
        await self.currency.load()
        return self._prices.get(currency, default)

    def __getitem__(self, item: str) -> float:
        try:
            return self._prices[item.upper()]
        except KeyError:
            raise CurrencyNotFound("Desired target currency not found, make sure it's in desired_currencies "
                                   "and that cryptocompare.com supports it.")

    def __setitem__(self, key: str, value: float) -> None:
        self._prices[key.upper()] = value

    def __getattr__(self, item: str) -> float:
        return self[item]


class Currency:
    """
    Currency object
    """
    def __init__(self, symbol: str, cache: int=60, target_currencies: List[str]=None,
                 extra_information: bool=False) -> None:
        self.symbol = symbol.upper()
        self.cache = cache
        self.target_currencies = target_currencies or ['USD', 'BTC']
        self.extra_information = extra_information
        self.last_loaded: Union[bool, float] = False
        self.prices = Prices(self)
        self.extra_data: Dict[str, Any] = {}

    @property
    def image_url(self) -> str:
        """Available only if extra_information is True - url to a image of currency's logo"""
        if not self.extra_data:
            return ''
        return f'https://www.cryptocompare.com{self.extra_data.get("ImageUrl")}'

    @property
    def name(self) -> str:
        """Available only if extra_information is True - name of the currency (e.g. Bitcoin from BTC)"""
        return self.extra_data.get('CoinName', '')

    async def load(self) -> None:
        """Loads the data if they are not cached"""
        tasks: List[Awaitable[Any]] = []
        if not self.last_loaded:
            if self.extra_information:
                tasks.append(fetch_coin_list())
            if self.last_loaded < self.last_loaded + self.cache:
                tasks.append(self.__load())

        await asyncio.gather(*tasks)

        if self.extra_information:
            extra_data = await fetch_coin_list()
            self.extra_data = extra_data.get(self.symbol, {})
        self.last_loaded = time.time()

    async def __load(self) -> None:
        json_data = await fetch_price_data([self.symbol], self.target_currencies)
        self.prices._prices.update(json_data)


class Currencies:
    """
    Wrapper around currencies.

    Paramaters will propagate to all currencies gotten through this wrapper.

    If you want to share state across modules, you should import currencies with lowercase
    and set their parameters manually.
    """
    def __init__(self, cache: int=60, target_currencies: List[str]=None,
                 extra_information: bool=False) -> None:
        self.currencies: Dict[str, Currency] = dict()
        self.cache = cache
        self.target_currencies = target_currencies or ['USD', 'BTC', 'ETH']
        self.extra_information = extra_information

    async def load_all(self) -> None:
        """Loads data for all currencies"""
        symbols = []
        for _, currency in self.currencies.items():
            symbols.append(currency.symbol)
        if self.extra_information:
            await fetch_coin_list()
        price_data = await fetch_price_data(symbols, self.target_currencies)
        for symbol, currency in self.currencies.items():
            currency.prices._prices.update(price_data.get(symbol, {}))
            currency.last_loaded = time.time()
            if self.extra_information:
                await currency.load()

    def add(self, *symbols: str) -> None:
        """Add a list of symbols for which to load prices"""
        for symbol in symbols:
            if symbol not in self.currencies:
                self.currencies[symbol] = Currency(symbol,
                                                   cache=self.cache,
                                                   target_currencies=self.target_currencies,
                                                   extra_information=self.extra_information)

    def __getitem__(self, item: str) -> Currency:
        """Gets a currency, if not present, will create one"""
        item = item.upper()
        if item not in self.currencies:
            self.currencies[item] = Currency(item, cache=self.cache, target_currencies=self.target_currencies,
                                             extra_information=self.extra_information)
        return self.currencies[item]

    def __getattr__(self, item: str) -> Currency:
        """Same as getitem, but accessible with dots"""
        return self[item]
