from datetime import datetime
from time import sleep

import config
import other
from database import db
import rates
import tg_bot
from netex_deal import fill_form
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
                nettex_price, target_min, target_max = rates.get_nettex_price(coin_id=asset_id, usdt=USDT)
                if not (target_min <= config.trading_amount_usdt <= target_max):
                    continue
                binance_rates = rates.get_binance_price(coin=asset)

                # Защита от отсутствия обмена валюты на обменнике
                if protection_no_currency_exchange(asset, binance_rates, nettex_price):
                    continue

                # Расчет профита с принтом результатов
                profit = other.calculate_profit(asset, binance_rates, nettex_price)

                data[asset, USDT] = profit
                sleep(0.2)

            end_dt = datetime.utcnow()
            profits = []

            for asset in sorted_assets:
                profits.append(data[asset, USDT])
            db.write_to_db([start_dt.isoformat(), end_dt.isoformat()] + profits)
            # sleep(5)

        profits = sorted(data.items(), key=lambda x: x[1], reverse=True)
        for (asset, USDT), profit in profits:
            if profit >= 0.7:
                try:
                    nettex_price, target_min, target_max = rates.get_nettex_price(coin_id=ASSETS[asset], usdt=USDT)
                    binance_price = rates.get_binance_price(coin=asset)
                    profit = other.calculate_profit(asset, binance_price, nettex_price)
                    if profit < 0.7:
                        continue
                    amount = config.trading_amount_usdt / binance_price

                    tg_bot.send_start_trading(asset, USDT, amount, profit)
                    starting_balance = tg_bot.get_binance_balance('USDT')
                    withdraw_details = tg_bot.get_withdraw_details(asset)
                    if not withdraw_details:
                        raise Exception('no withdraw_details')
                    opened_order = tg_bot.open_spot_order(asset, (amount + withdraw_details['fee']) * 1.002)
                    if not opened_order:
                        raise Exception('can\'t open order')
                    sleep(0.5)
                    amount = tg_bot.get_binance_balance(asset) - withdraw_details['fee']
                    binance_address = tg_bot.get_binance_depo_address(USDT)
                    netex_address = fill_form(amount, other.get_link_nettex(ASSETS[asset], USDT), binance_address)
                    tg_bot.withdraw(asset, withdraw_details['network'], netex_address, amount, withdraw_details['fee'])
                    tg_bot.send_trading_succeed(asset, USDT, amount, profit)
                    while True:
                        current_balance = tg_bot.get_binance_balance('USDT')
                        if current_balance > starting_balance - config.trading_amount_usdt:
                            tg_bot.send_msg(
                                f"Сообщение о том, что получен профит. Было {starting_balance} USDT, "
                                f"стало {current_balance}.",
                            )
                            break
                        sleep(15)
                except Exception as e:
                    tg_bot.send_trading_failed(f"SOS! SOS! ERROR: {e}")
                    raise


if __name__ == '__main__':
    bot()
