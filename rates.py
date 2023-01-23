from time import sleep

from requests import get, ConnectionError as CnxError
from json import loads

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------Nettex24
options = webdriver.ChromeOptions()
chrome_driver_binary = 'C:/Users/howar/chromedriver.exe'
options.binary_location = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe'

driver = Chrome(executable_path=chrome_driver_binary, options=options)


def get_nettex_rates(coin_id, usdt=188):

    url = f'https://netex24.net/api/exchangeDirection/getBy?source={coin_id}&target={usdt}'
    driver.get(url)
    driver.refresh()

    sleep(1)
    # WebDriverWait(driver, 10).until(
    #    EC.text_to_be_present_in_element_value(By.XPATH, "/html/body/pre/text()"))
    result = loads(driver.find_element(By.TAG_NAME, 'body').text)

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
