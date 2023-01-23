from webdriver import driver, driver_deal


# открыть netex, вбить нужные данные (включая адрес бинанса, куда засылать USDT), взять оттуда адрес нетекса

def fill_form(url, info):
    driver_deal.get(url)

    for field, value in info.items():
        driver_deal.find_element_by_name(field).send_keys(value)
    #driver_deal.find_element_by_xpath("//input[@type='submit']").click()


url = "https://netex24.net/#/ru/?source=165&target=188"
info = {'Сумма': 500}

fill_form(url, info)