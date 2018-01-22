# aiocrypto_prices

Very early version - API WILL CHANGE!

## Install

`$ pipenv install aiocrypto_prices`

or

`$ pip install aiocrypto_prices --user`

## Usage

Behind the scenes we are (currently) using cryptocompare's API,
which means all of the symbols need to be in their format and supported
by them.

### Simple

```python
>> from aiocrypto_prices import currencies
>> await currencies.ETH.prices.get('USD')
1053.28
```

### Advanced

Useful for loading things in parallel.

Careful, if you're not accessing the target price through `get`,
it might not reload after cache expires
```python
>> from aiocrypto_prices import currencies
>> currencies.add('BTC', 'ETH', 'IOT')
>> await currencies.load_all()
>> currencies.IOT.prices.USD
2.79
```
