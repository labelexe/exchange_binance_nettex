from hashlib import sha256
from hmac import new as hmac_new
from math import log, floor
from time import sleep
from urllib.parse import quote, urlencode

import requests
import config
import other


def send_msg(text, parse_mode=None):
    token = config.TG_TOKEN
    chat_id = config.admin_tg_id if hasattr(config, 'admin_tg_id') else '129658667'  # Mark by default

    text = quote(text)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': str(chat_id),
        'text': text,
        'disable_web_page_preview': True,
    }
    if parse_mode:
        params['parse_mode'] = parse_mode
    while True:
        r = requests.get(url, params=params)
        if r.status_code <= 400:
            break
        else:
            print(f"Failed request: {url}, {params}")
            sleep(0.5)
            raise Exception('request')


def get_server_time():
    while True:
        r = requests.get('https://api.binance.com/api/v1/time')
        if r.status_code < 400:
            return r.json()['serverTime']
        else:
            print(f"Failed request get_server_time")
            sleep(0.5)


def get_binance_depo_address(usdt_id):
    url = 'https://api.binance.com/sapi/v1/capital/deposit/address'
    params = {
        'coin': 'USDT',
        'network': 'BSC' if usdt_id == 188 else 'TRX',
        'timestamp': get_server_time(),
    }

    params['signature'] = hmac_new(
        config.binance_api_secret.encode('utf-8'), urlencode(params).encode('utf-8'), sha256,
    ).hexdigest()

    while True:
        r = requests.get(url, params=params, headers={'X-MBX-APIKEY': config.binance_api_key})
        if r.status_code < 400:
            return r.json()['address']
        else:
            print(f"Failed request: {url}, {params}")
            sleep(0.5)


def get_binance_balance(asset):
    url = 'https://api.binance.com/api/v3/account'
    params = {
        'timestamp': get_server_time(),
    }

    params['signature'] = hmac_new(
        config.binance_api_secret.encode('utf-8'), urlencode(params).encode('utf-8'), sha256,
    ).hexdigest()

    while True:
        r = requests.get(url, params=params, headers={'X-MBX-APIKEY': config.binance_api_key})
        if r.status_code < 400:
            return float([b['free'] for b in r.json()['balances'] if b['asset'] == asset][0])
        else:
            print(f"Failed request: {url}, {params}")
            sleep(0.5)


def get_withdraw_details(asset):
    network = {'TRX': 'TRX', 'LTC': 'LTC', 'DOGE': 'DOGE', 'BCH': 'BCH', 'DOT': 'DOT', 'ADA': 'ADA'}[asset]

    params = {'timestamp': get_server_time()}
    params['signature'] = hmac_new(
        config.binance_api_secret.encode('utf-8'), urlencode(params).encode('utf-8'), sha256,
    ).hexdigest()
    while True:
        r = requests.get(
            'https://api.binance.com/sapi/v1/capital/config/getall',
            headers={'X-MBX-APIKEY': config.binance_api_key},
            params=params,
        )
        if r.status_code < 400:
            r = r.json()
            break
        else:
            print(f"Failed request: api.binance.com/api/v3/exchangeInfo")
            sleep(0.5)

    network_status = {n.pop('network'): n for n in {f.pop('coin'): f for f in r}[asset]['networkList']}[network]
    return {
        'network': network, 'fee': float(network_status['withdrawFee']),
    } if network_status['withdrawEnable'] else None


def withdraw(asset, network, address, amount, network_fee):
    amount += float(network_fee)
    url = 'https://api.binance.com/sapi/v1/capital/withdraw/apply'
    params = {
        'coin': asset.upper(),
        'network': network.upper(),
        'address': address,
        'amount': str(amount),
        'timestamp': get_server_time(),
    }
    params['signature'] = hmac_new(
        config.binance_api_secret.encode('utf-8'), urlencode(params).encode('utf-8'), sha256,
    ).hexdigest()
    while True:
        r = requests.post(
            url,
            headers={'X-MBX-APIKEY': config.binance_api_key},
            params=params,
        )
        if r.status_code < 400:
            return True
        else:
            print(f"Failed request: {url}, {params}")
            sleep(0.5)


def open_spot_order(asset, quantity):
    while True:
        r = requests.get(
            'https://api.binance.com/api/v3/exchangeInfo',
            params={'symbol': f"{asset}USDT"},
        )
        if r.status_code < 400:
            r = r.json()
            break
        else:
            print(f"Failed request: api.binance.com/api/v3/exchangeInfo")
            sleep(0.5)
    if not r.get('symbols'):
        raise Exception('Bad response for binance get_symbol_status')
    pair = r['symbols'][0]
    trading = all([
        pair['status'] == 'TRADING',
        pair.get('isSpotTradingAllowed'),
        'SPOT' in pair['permissions'],
    ])
    filters = {f.pop('filterType'): f for f in pair['filters']}
    rules = dict(
        trading=trading,
        market_order='MARKET' in pair['orderTypes'],
        min_base_q=float(max(filters['LOT_SIZE']['minQty'], filters['MARKET_LOT_SIZE']['minQty'])),
        max_base_q=float(min(filters['LOT_SIZE']['maxQty'], filters['MARKET_LOT_SIZE']['maxQty'])),
        base_q_step=float(max(filters['LOT_SIZE']['stepSize'], filters['MARKET_LOT_SIZE']['stepSize'])),
    )
    assert rules['min_base_q'] <= abs(quantity) <= rules['max_base_q'], 'Too small quantity'
    digits_after_dot = -round(log(rules['base_q_step'], 10))
    quantity = round(floor(quantity * 10**digits_after_dot) / 10**digits_after_dot, digits_after_dot)

    url = 'https://api.binance.com/api/v3/order'
    params = {
        'timestamp': get_server_time(),
        'symbol': f"{asset}USDT",
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': quantity,
    }
    params['signature'] = hmac_new(
        config.binance_api_secret.encode('utf-8'), urlencode(params).encode('utf-8'), sha256,
    ).hexdigest()
    while True:
        r = requests.post(
            url,
            headers={'X-MBX-APIKEY': config.binance_api_key},
            params=params,
        )
        if r.status_code < 400:
            return True
        else:
            print(f"Failed request: {url}, {params}")
            sleep(0.5)


def send_report(buddy_id, asset, asset_id, usdt_id, profit):
    binance_address = get_binance_depo_address(asset)
    text = f"""связка #{buddy_id} = {profit}%
1) скопируй адрес binance:
{binance_address}
2) зайди на netex:
{other.get_link_nettex(asset_id, usdt_id)}
3) ответь мне сообщением:
{buddy_id} {{адрес кошелька netex}}"""
    send_msg(text)


def send_start_trading():
    pass


def send_trading_succeed():
    pass


def send_trading_failed(text):
    pass
