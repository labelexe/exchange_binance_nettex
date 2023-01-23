from time import sleep

from selenium.common import NoSuchElementException, ElementNotInteractableException

import config
from webdriver import driver_deal as conductor
from selenium.webdriver.common.by import By


def get_el(by, rule):
    for i in range(100):
        try:
            el = conductor.find_element(by, rule)
            if el.is_displayed() and el.is_enabled():
                return el
        except (NoSuchElementException, ElementNotInteractableException):
            sleep(0.2)
    raise Exception('things are going bad')


# открыть netex, вбить нужные данные (включая адрес бинанса, куда засылать USDT), взять оттуда адрес нетекса
def fill_form(amount, url, binance_address):
    conductor.get(url)

    el = get_el(By.XPATH, "//span[contains(text(), 'Сумма')]/parent::div/following-sibling::div//input")
    el.clear()
    el.send_keys(str(amount))

    el = get_el(By.XPATH, "//span[contains(text(), 'Адрес')]/parent::div/following-sibling::div//input")
    el.clear()
    el.send_keys(binance_address)

    el = get_el(By.XPATH, "//span[contains(text(), 'Ваш номер')]/parent::div/following-sibling::div//input")
    el.clear()
    el.send_keys(config.netex_phone)

    el = get_el(By.XPATH, "//span[contains(text(), 'Электронная почта')]/parent::div/following-sibling::div//input")
    el.clear()
    el.send_keys(config.netex_email)

    sleep(0.2)
    el = get_el(By.XPATH, "//button[contains(text(), 'Понятно')]")
    el.click()

    sleep(1)
    el = get_el(By.XPATH, "//span[contains(text(), 'Перейти к оплате')]/parent::span/parent::button")
    el.click()

    el = get_el(By.XPATH, "//h3[contains(text(), 'На кошелек')]/following-sibling::div")
    return el.text.split()[0]  # netex_address


if __name__ == '__main__':
    fill_form(888.14, "https://netex24.net/#/ru/?source=165&target=173", 'TYCiphUzDTzjZCKVSMmXaYAupFi4XTjAST')
