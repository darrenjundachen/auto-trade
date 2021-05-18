from keys import *
import requests
from datetime import datetime
from utils import datetime_to_timestamp
import hmac
import hashlib
from keys import api_key, secret_key

base = "https://api.binance.com/api/v3"
symbo = "BTCUSDT"

# POST /api/v3/order


def get_signature(body):
    body_str = ""
    for item in body.items():
        body_str += f"{item[0]}={item[1]}&"
    body_str = body_str[0 : len(body_str) - 1]
    return hmac.new(
        secret_key.encode("utf-8"), body_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def get_order_books():
    """
    bids: buy orders
    asks: sell orders
    """
    res = requests.get(f"{base}/depth", params={"symbol": symbo, "limit": 100})
    return res.json()


def get_accounnt_information():
    params = {"timestamp": datetime_to_timestamp(datetime.now())}
    params["signature"] = get_signature(params)
    res = requests.get(
        f"{base}/account", params=params, headers={"X-MBX-APIKEY": api_key}
    )
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
            "endTime": datetime_to_timestamp(end) if isinstance(end, datetime) else end,
            "limit": 1000,
        },
    )
    return res.json()


print(get_accounnt_information())