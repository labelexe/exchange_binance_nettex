# Защита от отсутствия обмена валюты на обменнике
# Если вместо курса где-то вернулся None, функция вернет 1
def protection_no_currency_exchange(asset, rate, rate2):
    if not (rate and rate2):
        print(f': {asset}\n'
              f'binance_rates: {rate} nettex_rates: {rate2}')
        return 1