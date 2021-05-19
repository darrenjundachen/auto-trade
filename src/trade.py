import time
from enum import Enum
from utils import log, sample_log, datetime_to_timestamp, round_decimals_down, send_heart_beat
from binance_api import (
    get_klines,
    get_order_books,
    get_account_information,
    TradeType,
    create_order,
    base_currency,
    target_currency,
)
from datetime import datetime, timedelta


class Status(Enum):
    WAITING_BUYING = 1
    BELOW_BUYING = 2
    WAITING_SELLING = 3
    OVER_SELLING = 4


def get_balance(currency):
    balances = get_account_information()["balances"]
    for balance in balances:
        if balance["asset"] == currency:
            return float(balance["free"])


def get_base_balance():
    return get_balance(base_currency)


def get_target_balance():
    return get_balance(target_currency)


def get_peak_price(peak_period):
    """
    Get peak from a peak_period back until now
    """
    end = datetime.now()
    start = end - timedelta(hours=peak_period)
    klines = get_klines(start, end, interval="5m")
    return float(max(klines, key=lambda x: x[2])[2])


def get_current_selling_price():
    """
    I'm buying BTC, so get the current selling price
    """
    total_base_amount = get_base_balance()
    asks = get_order_books()["asks"]
    for ask in asks:
        price = float(ask[0])
        target_amount = float(ask[1])
        base_amount = price * target_amount
        total_base_amount -= base_amount
        if total_base_amount <= 0:
            return price


def get_current_buying_price():
    """
    I'm selling BTC, so get the current buying price
    """
    total_target_amount = get_target_balance()
    asks = get_order_books()["bids"]
    for ask in asks:
        price = float(ask[0])
        target_amount = float(ask[1])
        total_target_amount -= target_amount
        if total_target_amount <= 0:
            return price


def sell_all(price):
    target_balance = get_target_balance()
    res = create_order(round_decimals_down(target_balance, 6), price, TradeType.SELL)
    return res["status"] == "FILLED"


def buy_all(price):
    base_balannce = get_base_balance()
    res = create_order(
        round_decimals_down(base_balannce / price, 6), price, TradeType.BUY
    )
    return res["status"] == "FILLED"


def trade():
    # Config
    buy_period = 12  # Count within 12 hours
    buy_point = 1.04  # Drop 1.04 to start buying
    buy_rise_to_execute = (
        1.002  # Rise 1.002 to exute the buy (To prevent buying when droppping)
    )
    sell_point = 1.02  # Increase 1.02 to meet target
    sell_drop_to_execute = (
        1.002  # Drop 0.002 from target to sell (To Prevent selling when rising)
    )
    sell_waiting_time = 48  # Wait for 48 hours until drop sell

    # Run time data
    status = Status.WAITING_BUYING
    sell_point_price = None
    drop_time = datetime.now() + timedelta(hours=sell_waiting_time)

    while True:
        send_heart_beat()
        if status == Status.WAITING_BUYING:
            peak_price = get_peak_price(buy_period)
            current_selling_price = get_current_selling_price()
            if peak_price > current_selling_price * buy_point:
                log(
                    f"Reached buy point, changed status to below buying. Peak: {peak_price}, Current Selling: {current_selling_price}"
                )
                current_lowest_price = current_selling_price
                status = Status.BELOW_BUYING
            else:
                sample_log(
                    f"[WAITING_BUYING] Waiting for the price to drop. Peak: {peak_price}, Current Selling: {current_selling_price}",
                    f"waiting_price_drop_buying_point",
                )
        elif status == Status.BELOW_BUYING:
            current_selling_price = get_current_selling_price()
            if current_selling_price < current_lowest_price:
                current_lowest_price = current_selling_price
                sample_log(
                    f"[BELOW_BUYING] Found a new low point. Still waiting. Current lowest: {current_lowest_price}",
                    "waiting_price_rise_buy_rise_to_execute",
                    rate=10,
                )
            elif current_selling_price > current_lowest_price * buy_rise_to_execute:
                # Time to buy
                if buy_all(current_selling_price):
                    status = Status.WAITING_SELLING
                    sell_point_price = current_selling_price * sell_point
                    drop_time = datetime.now() + timedelta(hours=sell_waiting_time)
                    log(f"Bought with price {current_selling_price}")
                else:
                    log(f"*Failed* to buy with price {current_selling_price}")
            else:
                sample_log(
                    f"[BELOW_BUYING] Waiting for the price to rise a bit. Current lowest: {current_lowest_price}, Current Selling: {current_selling_price}",
                    "waiting_price_rise_buy_rise_a_bit",
                    rate=10,
                )
        elif status == Status.WAITING_SELLING:
            current_buying_price = get_current_buying_price()
            if current_buying_price > sell_point_price:
                status = Status.OVER_SELLING
                current_highest_price = current_buying_price
                log(f"Reached sell point {current_buying_price}")
            elif datetime.now() > drop_time:
                # Time to drop sell
                if sell_all(current_buying_price):
                    status = Status.WAITING_BUYING
                    current_base_balance = get_base_balance()
                    log(
                        f"Drop sold with price {current_buying_price}, current balance: f{current_base_balance}"
                    )
                else:
                    log(f"*Failed* to sell with price {current_buying_price}")
            else:
                sample_log(
                    f"[WAITING_SELLING] Waiting for the price to rise. Sell point price: {sell_point_price}, Current buying: {current_buying_price}",
                    f"waiting_price_rise_sell_point",
                )
        elif status == Status.OVER_SELLING:
            current_buying_price = get_current_buying_price()
            if current_buying_price >= current_highest_price:
                current_highest_price = current_buying_price
                sample_log(
                    f"[OVER_SELLING] Found a new high point. Still waiting. Current highest: {current_highest_price}",
                    "waiting_price_rise_sell_rounnd_new_high",
                    rate=10,
                )
            elif current_buying_price * sell_drop_to_execute < current_highest_price:
                # Time to sell
                if sell_all(current_buying_price):
                    status = Status.WAITING_BUYING
                    current_base_balance = get_base_balance()
                    log(
                        f"Sold with price {current_buying_price}, current balance: {current_base_balance}"
                    )
                else:
                    log(f"*Failed* to sell with price {current_buying_price}")
            else:
                sample_log(
                    f"[OVER_SELLING] Waiting for the price to drop a bit. Current highest: {current_highest_price}, Current buying: {current_buying_price}",
                    "waiting_price_rise_sell_rise_to_execute",
                    rate=10,
                )
        else:
            raise Exception("Status not supported")

        time.sleep(1)


trade()
