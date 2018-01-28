import pytest

# TODO mock the http responses


@pytest.mark.asyncio
async def test_single_get(currencies, symbol_from, symbol_to):
    """
    >> from aiocrypto_prices import currencies
    >> await currencies.ETH.prices.get('USD')
    1053.28
    """
    resp = await getattr(currencies, symbol_from).prices.get(symbol_to)
    assert isinstance(resp, float)


@pytest.mark.asyncio
async def test_load_all(currencies, symbols, symbol_to):
    """
    >> from aiocrypto_prices import currencies
    >> currencies.add('BTC', 'ETH', 'IOT')
    >> await currencies.load_all()
    >> currencies.IOT.prices.USD
    2.79
    """
    currencies.target_currencies = symbols
    currencies.add(*symbols)
    await currencies.load_all()
    for symbol in symbols:
        assert isinstance(getattr(getattr(currencies, symbol).prices, symbol_to), float)
