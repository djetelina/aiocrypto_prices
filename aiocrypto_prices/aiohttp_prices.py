from typing import List, Any, Dict

import asyncio

from aiocrypto_prices._api_requests import fetch_price_data


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
            self.currency.target_currencies.append(currency)
        await self.currency.load()
        return self._prices.get(currency, default)

    def __getitem__(self, item: str) -> float:
        try:
            return self._prices[item]
        except KeyError:
            raise Exception("Desired target currency not found, make sure it's in desired_currencies "
                            "and that cryptocompare.com supports it.")

    def __setitem__(self, key: str, value: float) -> None:
        self._prices[key] = value

    def __getattr__(self, item: str) -> float:
        return self[item]


class Currency:
    """
    Currency object
    """
    def __init__(self, symbol, cache: int=60, target_currencies: List[str]=None) -> None:
        self.symbol = symbol
        self.cache = cache
        self.target_currencies = target_currencies or ['USD', 'BTC']
        self.last_loaded = False
        self.prices = Prices(self)
        # TODO figure out how to get self.name - rich parameter?

    async def load(self) -> None:
        """Loads the data if they are not cached"""
        if self.last_loaded or self.last_loaded < self.last_loaded + self.cache:
            await self.__load()

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
    def __init__(self, cache: int=60, target_currencies: List[str]=None) -> None:
        self.currencies: Dict[str, Currency] = dict()
        self.cache = cache
        self.target_currencies = target_currencies or ['USD', 'BTC']

    async def load_all(self) -> 'Currencies':
        """Loads data for all currencies"""
        # TODO load all in a single request
        tasks = []
        for _, currency in self.currencies.items():
            tasks.append(currency.load())
        await asyncio.gather(*tasks)
        return self

    def add(self, symbols: List[str]) -> None:
        """Add a list of symbols for which to load prices"""
        for symbol in symbols:
            if symbol not in self.currencies:
                self.currencies[symbol] = Currency(symbol,
                                                   cache=self.cache,
                                                   target_currencies=self.target_currencies)

    def __getitem__(self, item: str) -> Currency:
        """Gets a currency, if not present, will create one"""
        if item not in self.currencies:
            self.currencies[item] = Currency(item, cache=self.cache, target_currencies=self.target_currencies)
        return self.currencies[item]

    def __getattr__(self, item: str) -> Currency:
        """Same as getitem, but accessible with dots"""
        return self[item]
