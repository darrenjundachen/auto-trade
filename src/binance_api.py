from keys import *
import requests
from datetime import datetime
from utils import datetime_to_timestamp

base = "https://api.binance.com/api/v3"
symbo = "BTCUSDT"


def get_order_books():
    """
    bids: buy orders
    asks: sell orders
    """
    res = requests.get(f"{base}/depth", params={"symbol": symbo, "limit": 10})
    return res.json()


def get_klines(start, end):
    res = requests.get(
        f"{base}/klines",
        params={
            "symbol": symbo,
            "interval": "1m",
            "startTime": datetime_to_timestamp(start)
            if isinstance(start, datetime)
            else start,
            "endTime": datetime_to_timestamp(end)
            if isinstance(end, datetime)
            else end,
            "limit": 1000,
        },
    )
    return res.json()
