import requests
import asyncio
import aiohttp


async def get_coin_price(coin: str, base_url: str) -> float | None:
    #base_url = "https://api.binance.com/api/v3"
    url = "/ticker/price"

    params = {
        "symbol": coin,
    }

    await asyncio.sleep(0)

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + url, params=params) as response:

            if response.status != 200:
                return None

            data = await response.json()

    return data
    #return float(data["price"])


