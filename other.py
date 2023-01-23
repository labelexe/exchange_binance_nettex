# Вычисляет и выводит % профита
from math import floor


def calculate_profit(coin, rate, rate2):
    p = 1 / rate * rate2
    profit = (p - 1) * 100  # percent
    profit = round(floor(profit * 100) / 100, 2)
    print(f"Yo bitch: {coin}: {profit}%")
    return profit


def get_link_nettex(coin_is, usdt=188):
    return f"https://netex24.net/#/ru/?source={coin_is}&target={usdt}"


def get_link_binance(coin):
    return f"https://www.binance.com/en/trade/{coin}_USDT"