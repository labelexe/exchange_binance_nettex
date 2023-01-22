# Вычисляет и выводит % профита
def calculate_profit(coin, rate, rate2):

    p = 1 / rate * rate2
    profit = (p - 1) * 100  # percent
    print(f"Yo bitch: {coin}: {round(profit, 2)}%")
    return profit


def get_link_nettex(coin_is, usdt=188):
    return f"https://netex24.net/#/ru/?source={coin_is}&target={usdt}"


def get_link_binance(coin):
    return f"https://www.binance.com/en/trade/{coin}_USDT"