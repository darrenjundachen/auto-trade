from keys import *
import requests
from datetime import datetime
from utils import datetime_to_timestamp
import hmac
import hashlib
from keys import api_key, secret_key
from enum import Enum

base = "https://api.binance.com/api/v3"
symbo = "BTCUSDT"
base_currency = "USDT"
target_currency = "BTC"

class TradeType(Enum):
    SELL = 1
    BUY = 2


def get_signature(body):
    body_str = ""
    for item in body.items():
        body_str += f"{item[0]}={item[1]}&"
    body_str = body_str[0 : len(body_str) - 1]
    return hmac.new(
        secret_key.encode("utf-8"), body_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def get_order_books(limit=100):
    """
    bids: buy orders
    asks: sell orders
    """
    res = requests.get(f"{base}/depth", params={"symbol": symbo, "limit": limit}, timeout=5)
    res.raise_for_status()
    return res.json()


def get_account_information():
    params = {"timestamp": datetime_to_timestamp(datetime.now())}
    params["signature"] = get_signature(params)
    res = requests.get(
        f"{base}/account", params=params, headers={"X-MBX-APIKEY": api_key}
    )
    res.raise_for_status()
    return res.json()


def get_klines(start, end, interval="1m"):
    res = requests.get(
        f"{base}/klines",
        params={
            "symbol": symbo,
            "interval": interval,
            "startTime": datetime_to_timestamp(start)
            if isinstance(start, datetime)
            else start,
            "endTime": datetime_to_timestamp(end) if isinstance(end, datetime) else end,
            "limit": 1000,
        },
    )
    res.raise_for_status()
    return res.json()


def create_order(quantity, price, trade_type):
    params = {
        "symbol": symbo,
        "side": "BUY" if trade_type == TradeType.BUY else "SELL",
        "type": "LIMIT",
        "timeInForce": "FOK",
        "quantity": quantity,
        "price": price,
        "timestamp": datetime_to_timestamp(datetime.now()),
    }
    params["signature"] = get_signature(params)
    res = requests.post(
        f"{base}/order", params=params, headers={"X-MBX-APIKEY": api_key}
    )
    res.raise_for_status()
    return res.json()
