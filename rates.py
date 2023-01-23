from time import sleep

from requests import get, ConnectionError as CnxError
from json import loads

from selenium.webdriver.common.by import By

from netex_deal import get_el
from webdriver import driver


# -------------Nettex24
def get_nettex_rates(coin_id, usdt=188):

    url = f'https://netex24.net/api/exchangeDirection/getBy?source={coin_id}&target={usdt}'
    driver.get(url)

    result = loads(get_el(By.TAG_NAME, 'body').text)

    if coin_id in [158, 153, 160, 176]:
        return [result['rate']['rate'], result['targetLimits']['min'], result['targetLimits']['max']]
    else:
        return [1 / result['rate']['count'], result['targetLimits']['min'], result['targetLimits']['max']]


# -------------Binance
def get_binance_rates(coin):
    url = 'https://api.binance.com' + '/api/v3/depth' + f'?limit=1&symbol={coin}USDT'
    while True:
        try:
            response = get(url)
            if response.status_code >= 400:
                print(f"Failed request: {response.status_code} {url}")
                sleep(1)
                continue
            break
        except CnxError:
            print(f"Failed request: ConnectionError on {url}")
            sleep(1)
    return float(loads(get(url).content)['asks'][0][0])


if __name__ == '__main__':
    # res = get_bestchange_rates()
    # res = get_binance_rates()
    print()
