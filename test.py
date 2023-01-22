def create_report_text(asset, asset_id, usdt_id, profit, rate, rate2):

    text = (f"Yo bitch: {asset}: {round(profit, 2)}%"
            f"\n{rate}, {rate2}\n"
            f"Binance: {other.get_link_binance(asset)}\n"
            f"Nettex: {other.get_link_nettex(asset_id, usdt_id)}")

    return text