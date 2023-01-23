from selenium import webdriver

options = webdriver.ChromeOptions()
chrome_driver_binary = 'C:/Users/howar/chromedriver.exe'
options.binary_location = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe'

driver = webdriver.Chrome(executable_path=chrome_driver_binary, options=options)
driver_deal = webdriver.Chrome(executable_path=chrome_driver_binary, options=options)
