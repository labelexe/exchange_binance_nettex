from selenium import webdriver

import config

options = webdriver.ChromeOptions()
chrome_driver_binary = config.webdriver_binary
options.binary_location = config.options_binary

driver = webdriver.Chrome(executable_path=chrome_driver_binary, options=options)
driver_deal = webdriver.Chrome(executable_path=chrome_driver_binary, options=options)
