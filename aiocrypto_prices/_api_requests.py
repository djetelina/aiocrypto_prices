import asyncio
import json
from typing import List, Any, Dict

import aiohttp


_coin_list: Dict[str, Any] = {}


async def fetch(url: str) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
            return json.loads(text)


async def fetch_price_data(from_currencies: List[str], to_currencies: List[str], full: bool=False) -> Dict[str, Any]:
    if full:
        endpoint = 'pricemultifull'
        from_parameter = 'fsyms'
        if 'USD' not in to_currencies:
            to_currencies.append('USD')
    else:
        endpoint = 'pricemulti'
        from_parameter = 'fsyms'

    price_url = f'https://min-api.cryptocompare.com/data/{endpoint}?' \
                f'{from_parameter}={",".join(from_currencies)}&' \
                f'tsyms={",".join(to_currencies)}'
    resp = await fetch(price_url)
    if full:
        resp = resp.get('RAW')
    return resp


async def fetch_coin_list() -> Dict[str, Any]:
    global _coin_list
    async with asyncio.Lock():
        if not _coin_list:
            coin_list_url = 'https://min-api.cryptocompare.com/data/all/coinlist'
            _coin_list = await fetch(coin_list_url)
        return _coin_list['Data']
