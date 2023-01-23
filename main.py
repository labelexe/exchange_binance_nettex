from datetime import datetime
from time import sleep

import other
from database import db
import rates
import tg_bot
from protect import protection_no_currency_exchange

ASSETS = {'TRX': 165, 'LTC': 158, 'DOGE': 159, 'BCH': 160, 'DOT': 176, 'ADA': 184}
USDTS = [173, 188]  # 188 BEP20, 173 TRC20,

TABLEAU = {}  # {(asset, usdt_id): [buddy_id, profit, message_id], } or {('ETH', 173): [24, 2.54, 1026238]}


def bot():
    sorted_assets = sorted(ASSETS)
    db.create_db(sorted_assets)

    while True:
        start_dt = datetime.utcnow()
        data = {}

        for USDT in USDTS:

            for asset, asset_id in ASSETS.items():
                # take rates and min max price on changer
                nettex_rates, target_min, target_max = rates.get_nettex_rates(coin_id=asset_id, usdt=USDT)
                if not (target_min <= 500. <= target_max):
                    continue
                binance_rates = rates.get_binance_rates(coin=asset)

                # Защита от отсутствия обмена валюты на обменнике
                if protection_no_currency_exchange(asset, binance_rates, nettex_rates):
                    continue

                # Расчет профита с принтом результатов
                profit = other.calculate_profit(asset, binance_rates, nettex_rates)

                # Уведомление в тг если профит больше заданного процента
                if profit > 0.5:
                    if (asset, USDT) not in TABLEAU:
                        buddy_id = (max(i for i, p in TABLEAU.values()) + 1) if TABLEAU else 1
                        TABLEAU[asset, USDT] = [buddy_id, profit]
                        tg_bot.send_report(buddy_id, asset, asset_id, USDT, profit)
                    else:
                        buddy = TABLEAU[asset, USDT]
                        if buddy[1] != profit:
                            buddy[1] = profit

                data[asset] = profit
                sleep(0.2)

            end_dt = datetime.utcnow()
            profits = []

            for asset in sorted_assets:
                profits.append(data[asset])
            db.write_to_db([start_dt.isoformat(), end_dt.isoformat()] + profits)
            # sleep(5)

        profits = sorted(data.items(), key=lambda x: x[1], reverse=True)
        if profits:
            best_asset, best_profit = profits[0]
            if best_profit >= 0.7:
                # написать в тг, что пробуем отработать
                # снова проверить, что связка работает (перезагрузить курсы чисто для этой связки)
                # купить валюту на споте (с поправкой на коммиссию спота)
                # открыть netex, вбить нужные данные (включая адрес бинанса, куда засылать USDT), взять оттуда адрес нетекса
                # вывести с бинанса бабки на адрес нетекса
                # написать в тг, что отработали
                pass


if __name__ == '__main__':
    bot()
