from datetime import datetime
from time import sleep

import other
from database import db
import rates
import tg_bot
from protect import protection_no_currency_exchange

ASSETS = {'TRX': 165, 'LTC': 158, 'ETH': 153, 'DOGE': 159, 'BCH': 160, 'DOT': 176, 'ADA': 184, 'SHIB': 185}
USDTS = [173, 188]  # 188 BEP20, 173 TRC20,


def bot():
    sorted_assets = sorted(ASSETS)
    db.create_db(sorted_assets)

    while True:
        start_dt = datetime.utcnow()
        data = {}

        for USDT in USDTS:

            for asset, asset_id in ASSETS.items():
                nettex_rates = rates.get_nettex_rates(coin_id=asset_id, usdt=USDT)
                binance_rates = rates.get_binance_rates(coin=asset)

                # Защита от отсутствия обмена валюты на обменнике
                if protection_no_currency_exchange(asset, binance_rates, nettex_rates):
                    continue

                # Расчет профита с принтом результатов
                profit = other.calculate_profit(asset, binance_rates, nettex_rates)

                # Уведомление в тг если профит больше заданного процента
                if profit > 0.5:
                    tg_bot.send_report(asset, asset_id, USDT, profit, binance_rates, nettex_rates)

                data[asset] = profit
                sleep(0.2)

            end_dt = datetime.utcnow()
            profits = []

            for asset in sorted_assets:
                profits.append(data[asset])
            db.write_to_db([start_dt.isoformat(), end_dt.isoformat()] + profits)
            # sleep(5)


if __name__ == '__main__':
    bot()
