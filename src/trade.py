import time
from enum import Enum
from utils import log, datetime_to_timestamp
from binance_api import get_klines, get_order_books
from datetime import datetime, timedelta


class Status(Enum):
    BUYING = 1
    WAITTING_TARGET = 2
    OVER_TARGET = 3


class TradeType(Enum):
    SELL = 1
    BUY = 2


def get_peak(peak_period):
    """
    Get peak from a peak_period back until now
    """
    end = datetime.now()
    start = end - timedelta(hours=peak_period)
    klines = get_klines(start, end, interval="5m")
    return max(klines, key=lambda x: x[2])[2]


def get_current_selling_price(total_base_amount):
    """
    I'm buying BTC, so get the current selling price
    """
    current_total = total_base_amount
    asks = get_order_books()["asks"]
    for ask in asks:
        price = float(ask[0])
        target_amount = float(ask[1])
        base_amount = price * target_amount
        current_total -= base_amount
        print(f'{price} {target_amount} {base_amount}')
        if current_total <= 0:
            return price

def get_current_buying_price(total_target_amount):
    """
    I'm selling BTC, so get the current buying price
    """
    current_total = total_target_amount
    asks = get_order_books()["asks"]
    for ask in asks:
        price = float(ask[0])
        target_amount = float(ask[1])
        current_total -= target_amount
        print(f'{price} {target_amount}')
        if current_total <= 0:
            return price

def trade():
    peak_percentage = 1.04  # Drop 1.04 buy in
    peak_period = 12  # Count within 12 hours
    target_profit = 1.02  # Increase 1.02 to meet target
    target_peak_drop_percentage = 1.002  # Drop 0.002 from target to sell
    max_waiting_time = 48  # Wait for 48 hours untile drop sell

    print(get_current_selling_price(20000))
    #print(get_current_buying_price(0.5))

    # while True:
    #     time.sleep(2)
    #     log(f"target_peak_drop_percentage")


trade()
