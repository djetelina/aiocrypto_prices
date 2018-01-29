from typing import List

import pytest

from aiocrypto_prices import Currencies, Currency

# TODO mock the http responses

pytestmark = pytest.mark.asyncio


async def test_single_get(currencies: Currencies, symbol_from: str, symbol_to: str):
    """
    >>> from aiocrypto_prices import currencies
    >>> await currencies.ETH.prices.get('USD')
    1053.28
    """
    resp = await getattr(currencies, symbol_from).prices.get(symbol_to)
    assert isinstance(resp, float)


async def test_load_all(currencies: Currencies, symbols: str, symbol_to: str):
    """
    >>> from aiocrypto_prices import currencies
    >>> currencies.add('BTC', 'ETH', 'IOT')
    >>> await currencies.load_all()
    >>> currencies.IOT.prices.USD
    2.79
    """
    currencies.target_currencies = symbols
    currencies.add(*symbols)
    await currencies.load_all()
    for symbol in symbols:
        assert isinstance(getattr(getattr(currencies, symbol).prices, symbol_to), float)


async def test_full(currencies: Currencies, symbol_from: str, symbol_to: str):
    """
    >>> from aiocrypto_prices import currencies
    >>> currencies.full = True
    >>> currencies.target_currencies = ['USD']
    >>> currency = currencies.ETH
    >>> await currency.load()
    >>> currency.market_cap
    121201618306.0
    >>> currency.supply
    97271786.0
    """
    currencies.full = True
    currencies.target_currencies = [symbol_to]
    currency: Currency = getattr(currencies, symbol_from)
    await currency.load()
    assert isinstance(currency.market_cap, float)
    assert isinstance(currency.supply, float)


async def test_full_multiple(symbols: List[str], symbol_to: str):
    """
    >>> from aiocrypto_prices import Currencies
    >>> currencies = Currencies(full=True, target_currencies=['USD'])
    >>> currencies.add('ETH', 'ZEC')
    >>> await currencies.load_all()
    >>> currencies.ETH.market_cap
    121201618306.0
    >>> currencies.ZEC.supply
    3158456.0
    """
    currencies = Currencies(full=True, target_currencies=[symbol_to])
    currencies.add(*symbols)
    await currencies.load_all()
    for symbol in symbols:
        currency: Currency = getattr(currencies, symbol)
        assert isinstance(currency.market_cap, float)
        assert isinstance(currency.supply, float)
