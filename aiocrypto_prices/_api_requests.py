import json
from typing import List, Any, Dict

import aiohttp


async def fetch_price_data(from_currencies: List[str], to_currencies: List[str]) -> Dict[str, Any]:
    API_URL = f'https://min-api.cryptocompare.com/data/price?' \
              f'fsym={",".join(from_currencies)}&' \
              f'tsyms={",".join(to_currencies)}'
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            text = await resp.text()
            return json.loads(text)
