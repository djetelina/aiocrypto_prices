# aiocrypto_prices

Very early version - API WILL CHANGE!

If you happen to stumble upon this library, please provide any and all feedback
through any means comfortable to you.

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

### Setting up extra options

```python
>>> from aiocrypto_prices import currencies
>>> currencies.cache = 120  # 2 minute cache
>>> currencies.target_currencies.append('EUR') # In addition to defaults, let's fetch EUR too.
>>> currencies.extra_information = True	# Get name and url of a logo
```

or

```python
>>> from aiocrypto_prices import Currencies
>>> currencies = Currencies(cache=120, target_currencies=['USD', 'EUR'], extra_information=True)
```

## Changelog

### 0.0.3

* extra_information parameter was renamed to human
* new paramter 'full' providing market cap and supply
	* More data should be provided with 'full', but requires a redesign of Prices class

## TODO

* all the TODOs scattered around the code
* All the available information cryptocompare offers
* Assign amount in that currency? - perhaps aiocrypto_folio?
	* Implement adding together currencies of the same symbol and possibly other interactions



* aiocrypto_exchanges
* aiocrypto_pools