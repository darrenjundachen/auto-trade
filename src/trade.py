import time
from enum import Enum
from utils import log, datetime_to_timestamp, round_decimals_down
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
    BUYING = 1
    WAITTING_TARGET = 2
    OVER_TARGET = 3


def get_balance(currency):
    balances = get_account_information()["balances"]
    for balance in balances:
        if balance["asset"] == currency:
            return float(balance["free"])


def get_base_balance():
    return get_balance(base_currency)


def get_target_balance():
    return get_balance(target_currency)


def get_peak(peak_period):
    """
    Get peak from a peak_period back until now
    """
    end = datetime.now()
    start = end - timedelta(hours=peak_period)
    klines = get_klines(start, end, interval="5m")
    return max(klines, key=lambda x: x[2])[2]


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
    return res['status'] == 'FILLED'

def buy_all(price):
    base_balannce = get_base_balance()
    res = create_order(round_decimals_down(base_balannce / price, 6), price, TradeType.BUY)
    return res['status'] == 'FILLED'


def trade():
    # Config
    peak_percentage = 1.04  # Drop 1.04 buy in
    peak_period = 12  # Count within 12 hours
    target_profit = 1.02  # Increase 1.02 to meet target
    target_peak_drop_percentage = 1.002  # Drop 0.002 from target to sell
    max_waiting_time = 48  # Wait for 48 hours untile drop sell

    # Default status
    status = Status.BUYING
    over_target_peak_price = None
    

    # print(get_base_balance())
    # print(get_target_balance())

    # print(get_account_information())
    # print(get_current_selling_price(20000))
    # print(get_current_buying_price(0.5))

    # while True:
    #     time.sleep(2)
    #     log(f"target_peak_drop_percentage")


trade()
