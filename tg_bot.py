from urllib.parse import quote

import requests
import config
import other


def send_msg(text):
    token = config.TG_TOKEN
    chat_id = '129658667'  # 129658667 Mark

    text = quote(text)
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + \
              "&text=" + text + "&disable_web_page_preview=true"
    results = requests.get(url_req)


def create_report_text(asset, asset_id, usdt_id, profit, rate, rate2):

    text = (f"Yo bitch: {asset}: {round(profit, 2)}%"
            f"\n{rate}, {rate2}\n"
            f"Binance: {other.get_link_binance(asset)}\n"
            f"Nettex: {other.get_link_nettex(asset_id, usdt_id)}")

    return text


def send_report(asset, asset_id, usdt_id, profit, rate, rate2):
    send_msg(create_report_text(asset, asset_id, usdt_id, profit, rate, rate2))
