def get_different(price_last: int | float, price_current: int | float) -> int | float:
    sub_dif = abs(price_last - price_current)
    result = sub_dif / price_current
    result_in_percent = result * 100
    return result_in_percent


def sub_persent(price: int | float, percent: int | float) -> int | float:
    one_percent = price / 100
    dif_in_percent = one_percent * percent
    result = price - dif_in_percent
    return round(result, 8)



#coin1 = [100, 200]
#print(get_different(coin1[0], coin1[1]))
