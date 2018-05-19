#!/usr/bin/env python3
import datetime
import toml
import requests

# Base currencies (noncrypto)
currencies = ['EUR', 'USD']

# Get all cryptocurrencies and their symbols that cryptocompare supports
cc_list = requests.get('https://www.cryptocompare.com/api/data/coinlist/').json()
for cc, _ in cc_list['Data'].items():
    currencies.append(cc)

prices = dict()
start = 0
batch_size = 60
while start < len(currencies):
    fsyms = ','.join(currencies[start:start+batch_size])
    prices.update(requests.get('https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms=USD'.format(fsyms)).json())
    start += batch_size

fallbacks = dict()
for symbol, price_data in prices.items():
    fallbacks[symbol] = price_data['USD']

with open('../aiocrypto_prices/fallbacks.tml', 'w') as f:
    toml.dump({'fallback_prices': fallbacks, 'updated': datetime.datetime.now()}, f)
