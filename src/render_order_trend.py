import time
from binance_api import get_order_books
from colorama import Fore
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.animation import FuncAnimation
from matplotlib.dates import DateFormatter, MinuteLocator
import sys
from tinydb import TinyDB, Query

if len(sys.argv) != 2:
    raise Exception("Invalid")

date_length_minutes = int(sys.argv[1])

db = TinyDB("../order_trend.json")
Item = Query()

items = []


def aninmate(i):
    last_valid = datetime.now() - timedelta(minutes=date_length_minutes)
    items = db.search(Item.time > last_valid.strftime("%Y-%m-%dT%H:%M:%S"))

    items = [
        {"x": datetime.strptime(item["time"], "%Y-%m-%dT%H:%M:%S"), "y": item["figure"]}
        for item in items
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


ani = FuncAnimation(plt.gcf(), aninmate, interval=8000)
plt.show()