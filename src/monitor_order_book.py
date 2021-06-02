import time
from binance_api import get_order_books
from colorama import Fore
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.animation import FuncAnimation
from matplotlib.dates import DateFormatter, MinuteLocator
import sys

if len(sys.argv) != 2:
    raise Exception("Invalid")

date_length_minutes = int(sys.argv[1])


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


items = []


def aninmate(i):
    global items

    items.append(
        {"x": datetime.now(), "y": get_number()},
    )

    items = [
        item
        for item in items
        if item["x"] > (datetime.now() - timedelta(minutes=date_length_minutes))
    ]

    positive_items = [item for item in items if item["y"] >= 0]
    negative_items = [item for item in items if item["y"] < 0]

    plt.cla()
    plt.bar(
        [item["x"] for item in positive_items],
        [item["y"] for item in positive_items],
        color="g",
        width=9 / 24 / 60 / 60,
    )
    plt.bar(
        [item["x"] for item in negative_items],
        [item["y"] for item in negative_items],
        color="r",
        width=9 / 24 / 60 / 60,
    )
    plt.gca().xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
    plt.gca().xaxis.set_major_locator(MinuteLocator(interval=1))
    plt.xticks(rotation=90)
    plt.grid()
    plt.title(f"{date_length_minutes} minutes")


ani = FuncAnimation(plt.gcf(), aninmate, interval=10000)
plt.show()