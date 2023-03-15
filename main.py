import asyncio
from get_stat import get_coin_price
from currency_calc import *
from datetime import timedelta, datetime
import settings
from itertools import cycle
import os

if not os.path.exists("err_log"):
    err_log = open("err_log", "w")

else:
    err_log = open("err_log", "a")

if not os.path.exists("log"):
    log = open("log", "w")

else:
    log = open("log", "a")

COINS = [settings.BTC_name, settings.ETH_name]


async def make_float(data: list[dict]) -> list[dict]:
    for ind, obj in enumerate(data):
        obj["price"] = round(float(obj["price"]), 8)
        data[ind] = obj

    return data


async def get_coin(data: list[dict], coin_name: str) -> tuple[dict] | None:
    for ind, obj in enumerate(data):
        if obj["symbol"] == coin_name:
            return data[ind]


async def get_coins(base_url: str) -> tuple[dict] | dict:
    tasks = list()
    for coin in COINS:
        tasks.append(
            asyncio.create_task(
                get_coin_price(
                    coin=coin,
                    base_url=base_url,
                ))
        )

    result = await asyncio.gather(*tasks)
    result = await make_float(result)

    return result


async def init_fake_db(url) -> dict:
    buf = await get_coins(url)
    db = dict()

    for obj in buf:
        db[obj["symbol"]] = obj["price"]

    db["time"] = datetime.now()

    return db


async def calculate_eth(storage: dict, eth: dict, btc: dict, action) -> dict:
    try:
        btc_last_price = storage[settings.BTC_name]
        eth_last_price = storage[settings.ETH_name]

    except KeyError:
        print("not enough data")
        storage[settings.BTC_name] = btc["price"]
        storage[settings.ETH_name] = eth["price"]
        storage["time"] = datetime.now()
        return

    btc_diff_perc = get_different(price_last=btc_last_price,
                                    price_current=btc["price"])

    #print("\n\nbtc last", btc_last_price,
            #"\nbtc now", btc["price"],
            #"\nbtc diff", btc_diff_perc)

    eth_without_error = sub_persent(price=eth["price"],
                                    percent=btc_diff_perc)

    eth_diff_perc = get_different(price_last=eth_last_price,
                                    price_current=eth_without_error)

    #print("\nlast eth", storage[settings.ETH_name],
            #"\neth", eth["price"],
            #"\npure eth", eth_without_error,
            #"\nperc diff", eth_diff_perc)

    message = str(datetime.now()) + "\nlast eth " + str(storage[settings.ETH_name]) + "\neth " + str(eth_without_error) + "\npercent different " + str(eth_diff_perc)

    if eth_diff_perc >= 1:
        message += "\nMORE THEN ONE PERCENT"
        action()

    message += "\n\n"

    log.write(message)
    log.flush()

    storage[settings.BTC_name] = btc["price"]
    storage[settings.ETH_name] = eth_without_error
    storage["time"] = datetime.now()

    return storage


async def main(base_url):
    global coins_last_price

    count = 0
    print("START", datetime.now())
    while True:
        await asyncio.sleep(settings.DELAY_sec)

        result = await get_coins(base_url)

        btc = await get_coin(result, settings.BTC_name)
        eth = await get_coin(result, settings.ETH_name)


        print(datetime.now(), eth["price"], end="\r")
        if (datetime.now() - coins_last_price["time"]) >= settings.DELTA:
            coins_last_price = await calculate_eth(storage=coins_last_price,
                                                   eth=eth,
                                                   btc=btc,
                                                   action=lambda: print(f"\t\t{datetime.now()}: MORE THEN ONE PERCENT")
                                                   )

            #print(coins_last_price)



if __name__ == "__main__":
    base_urls = ["https://api.binance.com/api/v3",
                 "https://api1.binance.com/api/v3",
                 "https://api2.binance.com/api/v3",
                 "https://api3.binance.com/api/v3",
                 "https://api4.binance.com/api/v3",
                 ]

    genegator = cycle(base_urls)
    url = next(genegator)
    coins_last_price: dict[str, float] = asyncio.run(init_fake_db(url))

    while True:
        try:
            asyncio.run(main(url))

        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            err_log.write(f"[!]ERROR {datetime.now()}: {e}\n")
            err_log.flush()
            url = next(genegator)
