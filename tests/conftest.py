import pytest
from _pytest.fixtures import SubRequest

from aiocrypto_prices import Currencies


@pytest.fixture(scope='function')
def currencies():
    return Currencies()


@pytest.fixture
def symbols():
    return ['USD', 'ETH', 'BTC', 'DOGE']


@pytest.fixture(params=symbols())
def symbol_from(request: SubRequest):
    return request.param


@pytest.fixture(params=symbols())
def symbol_to(request: SubRequest):
    return request.param
