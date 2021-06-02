import time
from binance_api import get_order_books
from colorama import Fore
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.animation import FuncAnimation
from matplotlib.dates import DateFormatter, MinuteLocator
from tinydb import TinyDB, Query
import sys

db = TinyDB('../order_trend.json')
Item = Query()

def get_number():
    order_books = get_order_books(limit=5000)
    bids = order_books["bids"]
    asks = order_books["asks"]
    rate = 1.04

    bid_total = 0
    bid_begin = float(bids[0][0])
    bid_end = bid_begin / rate
    for bid in bids:
        price = float(bid[0])
        amount = float(bid[1])
        if price < bid_end:
            break
        weight_price = price
        weight_price = weight_price - bid_end
        weight_price = weight_price ** 2
        bid_total += weight_price * amount

    ask_total = 0
    ask_begin = float(asks[0][0])
    ask_end = ask_begin * rate
    for ask in asks:
        price = float(ask[0])
        amount = float(ask[1])
        if price > ask_end:
            break
        weight_price = ask_end - price + ask_begin
        weight_price = weight_price - ask_begin
        weight_price = weight_price ** 2
        ask_total += weight_price * amount

    return round((bid_total - ask_total) / bid_total * 100, 2)

while True:
    now = datetime.now()
    last_valid_time = (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
    db.insert({'time': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 'figure': get_number()})
    db.remove(Item.time < last_valid_time)
    time.sleep(10)