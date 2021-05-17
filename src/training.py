from tinydb import TinyDB, Query
from datetime import datetime, timedelta
from colorama import Fore
import pymongo
from utils import datetime_to_timestamp, timestamp_to_datetime
from enum import Enum

client = pymongo.MongoClient("localhost", 27017)
db = client.trade

kline_buffer = []


def find_index(kline, start, end, target_time):
    if end - start <= 1:
        return start

    mid = int((start + end) / 2)

    if mid + 1 > end:
        return mid

    if (
        kline[mid]["open_time"] <= target_time
        and kline[mid + 1]["open_time"] >= target_time
    ):
        return mid

    if kline[mid]["open_time"] > target_time:
        return find_index(kline, start, mid, target_time)
    else:
        return find_index(kline, mid, end, target_time)


def get_klines(begin, end):
    global kline_buffer

    if (
        not len(kline_buffer)
        or kline_buffer[0]["open_time"] > datetime_to_timestamp(begin)
        or kline_buffer[-1]["open_time"] < datetime_to_timestamp(end)
    ):
        kline_buffer = list(
            db.klines.find(
                {
                    "$and": [
                        {"open_time": {"$gte": datetime_to_timestamp(begin)}},
                        {
                            "open_time": {
                                "$lte": datetime_to_timestamp(end + (end - begin) * 10)
                            }
                        },
                    ]
                }
            ).sort("open_time", 1)
        )

    begin_index = find_index(
        kline_buffer, 0, len(kline_buffer) - 1, datetime_to_timestamp(begin)
    )
    end_index = find_index(
        kline_buffer, 0, len(kline_buffer) - 1, datetime_to_timestamp(end)
    )

    return kline_buffer[begin_index : end_index + 1]

class Status(Enum):
    BUYING = 1
    WAITTING_TARGET = 2
    OVER_TARGET = 3

def simulate(
    current,
    peak_percentage,
    peak_period,
    target_profit,
    target_peak_drop_percentage,
    max_waiting_time,
    fee_rate=0.001,
):
    status = Status.BUYING
    base_currency_amount = 1.0
    target_currency_amount = 0
    exit_datetime = datetime.now()

    # One loop for one minute
    while current < exit_datetime:
        klines = get_klines(current - timedelta(hours=peak_period), current)
        current_line = klines[-1]
        current_time = timestamp_to_datetime(current_line["open_time"])
        current_price = current_line["open"]

        if status == Status.BUYING:
            # Get last peak_period klines
            peak_line = max(klines, key=lambda x: x["high"])

            # Buy current
            if (peak_line["high"] / current_line["high"]) > peak_percentage:
                # Buy in
                fees = fee_rate * base_currency_amount
                target_currency_amount = base_currency_amount / current_price
                base_currency_amount = 0

                # Set status
                status = Status.WAITTING_TARGET
                target_price = current_price * target_profit
                drop_time = current_time + timedelta(
                    hours=max_waiting_time
                )  # Drop time when waiting target

                print(
                    Fore.WHITE
                    + f"[Bought]    {current_time} target: {round(target_currency_amount,4)}, current price: {round(current_price, 4)}",
                )
        elif status == Status.WAITTING_TARGET:
            if current_price >= target_price:
                status = Status.OVER_TARGET
                over_target_peak_price = current_price
            elif current_time > drop_time:
                # Drop sell
                base_currency_amount = target_currency_amount * current_price
                target_currency_amount = 0
                fees += fee_rate * base_currency_amount
                status = Status.BUYING

                print(
                    f"[Drop Sold] {current_time} base: {Fore.RED}{round(base_currency_amount,4)}{Fore.WHITE}, current price: {round(current_price, 4)}",
                )
        elif status == Status.OVER_TARGET:
            if current_price >= over_target_peak_price:
                over_target_peak_price = current_price
            elif current_price < over_target_peak_price * target_peak_drop_percentage:
                # Sell
                base_currency_amount = target_currency_amount * current_price
                target_currency_amount = 0
                fees += fee_rate * base_currency_amount
                status = Status.BUYING

                print(
                    f"[Sold]      {current_time} base: {Fore.GREEN}{round(base_currency_amount,4)}{Fore.WHITE}, current price: {round(current_price, 4)}",
                )

        else:
            raise Exception("Status not supported")

        current += timedelta(minutes=1)


simulate(datetime(2021, 1, 1), 1.04, 12, 1.02, (1 - 0.002), 48) 