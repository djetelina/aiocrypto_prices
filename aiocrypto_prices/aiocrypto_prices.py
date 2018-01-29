import asyncio
import time
from typing import List, Any, Dict, Union, Awaitable, Optional

from mypy_extensions import TypedDict

from aiocrypto_prices._api_requests import fetch_price_data, fetch_coin_list
from aiocrypto_prices.exceptions import CurrencyNotFound, UnfetchedInformation

CURRENCY_KWARGS = TypedDict('CurrencyKwargs', {
    'cache': int,
    'target_currencies': List[str],
    'full': bool,
    'historical': Optional[str],
    'human': bool
})


class Prices:
    """Prices object"""
    def __init__(self, currency: 'Currency') -> None:
        self._prices: Dict[str, float] = {}
        self._currency = currency

    async def get(self, target_currency: str, default: Any=None) -> Any:
        """
        Gets the price for a specified currency, if currency is not in target currencies,
        it's added there for the specific currency

        :param target_currency:     Currency to get converted price for
        :param default:             What to return if the desired currency is not found in fetched prices
        """
        target_currency = target_currency.upper()
        if target_currency not in self._currency.target_currencies:
            self._currency.target_currencies.append(target_currency)
        await self._currency.load()
        # TODO float should be in the dict from when it's put there -> stop using .update() with data from api
        return float(self._prices.get(target_currency, default))

    def __getitem__(self, item: str) -> float:
        try:
            return float(self._prices[item.upper()])
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
                 full: bool = False, historical: Optional[str] = None, human: bool = False) -> None:
        """
        :param symbol:              Symbol of the currency (e.g. ZEC) - will be converted to uppercase automatically
        :param cache:               Seconds to keep prices in cache
        :param target_currencies:   Which currencies to convert prices to
        :param full:                Whether to fetch full data, like change, market cap, volume etc.
        :param historical:          Whether to fetch movement data, either None, or 'minute', 'hour', 'day'
        :param human:               Whether to fetch information that concern humans (logo, full name)
        """
        self.symbol = symbol.upper()
        self.cache = cache
        self.target_currencies = target_currencies or ['USD', 'BTC']
        self.last_loaded: Union[bool, float] = False
        self.prices = Prices(self)
        self.full = full
        self.historical = historical
        self.human = human
        self.human_data: Dict[str, Any] = {}

    @property
    def image_url(self) -> str:
        """Available only if human is True - url to a image of currency's logo"""
        if not self.human:
            raise UnfetchedInformation('human must be True to fetch image_url')
        return f'https://www.cryptocompare.com{self.human_data.get("ImageUrl")}'

    @property
    def name(self) -> str:
        """Available only if human is True - name of the currency (e.g. Bitcoin from BTC)"""
        if not self.human:
            raise UnfetchedInformation('human must be True to fetch name')
        return self.human_data.get('CoinName', '')

    @property
    def supply(self) -> float:
        if not self.full:
            raise UnfetchedInformation('full must be True to fetch supply')
        return float(self.full_data['USD']['SUPPLY'])

    @property
    def market_cap(self) -> float:
        # TODO should be in self.prices
        if not self.full:
            raise UnfetchedInformation('full must be True to fetch market_cap')
        return float(self.full_data['USD']['MKTCAP'])

    def volume(self):
        raise NotImplementedError

    async def load(self) -> None:
        """Loads the data if they are not cached"""
        tasks: List[Awaitable[Any]] = []
        if not self.last_loaded:
            if self.human:
                tasks.append(fetch_coin_list())

        if not self.last_loaded or time.time() < self.last_loaded + self.cache:
            tasks.append(self.__load())

        await asyncio.gather(*tasks)

        if self.human and not self.human_data:
            extra_data = await fetch_coin_list()
            self.human_data = extra_data.get(self.symbol, {})
        self.last_loaded = time.time()

    async def __load(self) -> None:
        json_data = await fetch_price_data([self.symbol], self.target_currencies, full=self.full)
        if self.full:
            self.full_data = json_data.get(self.symbol)
            for tsym, data in self.prices._prices:
                if self.full_data.get(tsym):
                    self.prices._prices[tsym] = self.full_data.get(tsym).get('PRICE')
        else:
            self.prices._prices.update(json_data.get(self.symbol, {}))


class Currencies:
    """
    Wrapper around currencies.

    Paramaters will propagate to all currencies gotten through this wrapper.

    If you want to share state across modules, you should import currencies with lowercase
    and set their parameters manually.
    """
    def __init__(self, cache: int=60, target_currencies: List[str]=None,
                 full: bool=False, historical: Optional[str]=None, human: bool=False) -> None:
        """
        :param cache:               Seconds to keep prices in cache
        :param target_currencies:   Which currencies to convert prices to
        :param full:                Whether to fetch full data, like change, market cap, volume etc.
        :param historical:          Whether to fetch movement data, either None, or 'minute', 'hour', 'day'
                                    TODO https://min-api.cryptocompare.com/data/histominute?fsym=BTC&tsym=USD&limit=60&aggregate=3&e=CCCAGG
                                    TODO aggregate -> po kolika minutach, cas je v timestampech
                                    Bonusove argumenty v metode a vracet jen metodou?
        :param human:               Whether to fetch information that concern humans (logo, full name)
        """
        self.currencies: Dict[str, Currency] = dict()
        self.cache = cache
        self.target_currencies = target_currencies or ['USD', 'BTC', 'ETH']
        self.full = full
        self.historical = historical
        self.human = human

    async def load_all(self) -> None:
        """Loads data for all currencies"""
        symbols = []
        for _, currency in self.currencies.items():
            symbols.append(currency.symbol)
        if self.human:
            # This is done just once, as the contents don't change
            await fetch_coin_list()
        # TODO fetch only if at least one isn't cached
        price_data = await fetch_price_data(symbols, self.target_currencies, full=self.full)
        for symbol, currency in self.currencies.items():
            if self.full:
                currency.full_data = price_data.get(symbol)
            currency.prices._prices.update(price_data.get(symbol, {}))
            currency.last_loaded = time.time()
            if self.human:
                # Update the currency with already fetched extra information
                await currency.load()

    def add(self, *symbols: str) -> None:
        """Add to the list of symbols for which to load prices"""
        for symbol in symbols:
            if symbol not in self.currencies:
                self.currencies[symbol] = Currency(symbol, **self.__currency_kwargs)

    @property
    def __currency_kwargs(self) -> CURRENCY_KWARGS:
        """All kwargs that are propagated to individual currencies"""
        return {
            'cache': self.cache,
            'target_currencies': self.target_currencies,
            'full': self.full,
            'historical': self.historical,
            'human': self.human
        }

    def __getitem__(self, item: str) -> Currency:
        """Gets a currency, if not present, will create one"""
        item = item.upper()
        if item not in self.currencies:
            self.currencies[item] = Currency(item, **self.__currency_kwargs)
        return self.currencies[item]

    def __getattr__(self, item: str) -> Currency:
        """Same as getitem, but accessible with dots"""
        return self[item]
