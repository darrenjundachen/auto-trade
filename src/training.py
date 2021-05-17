from tinydb import TinyDB, Query
from datetime import datetime, timedelta
from colorama import Fore
import pymongo
from utils import datetime_to_timestamp, timestamp_to_datetime

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


def print_log(enabled, msg):
    if enabled:
        print(msg)


def simulate(
    current,
    peak_percentage,
    peak_period,
    target_profit,
    drop_time,
    fee_rate=0.001,
    ennanble_log=False,
):
    fees = 0
    base_pre_sold_amount = 0
    base_currency_amount = 1.0  # start from 1
    target_currency_amount = 0
    selling_price = None
    selling_list_time = None
    exit_datetime = datetime.now()
    profit_sold = 0
    drop_sold = 0
    bought = 0

    # One loop for one minute
    while current < exit_datetime:
        klines = get_klines(current - timedelta(hours=peak_period), current)
        current_line = klines[-1]
        current_time = timestamp_to_datetime(current_line["open_time"])
        current_price = current_line["open"]

        if selling_price:
            if current_price >= selling_price or (
                current_time - selling_list_time
            ) > timedelta(hours=drop_time):
                is_profit_sold = current_price >= selling_price
                base_currency_amount = target_currency_amount * current_price
                target_currency_amount = 0
                selling_price = None
                selling_list_time = None
                fees += fee_rate * base_currency_amount

                if is_profit_sold:
                    profit_sold += 1
                    print_log(
                        ennanble_log,
                        f"{Fore.GREEN}[Sold] {Fore.WHITE}{current_time} base: {base_currency_amount}, target: {target_currency_amount}, current price: {current_price}, sold price: {current_price}",
                    )
                else:
                    drop_sold += 1
                    print_log(
                        ennanble_log,
                        f"{Fore.RED}[Drop Sold] {Fore.WHITE}{current_time} base: {base_currency_amount}, target: {target_currency_amount}, current price: {current_price}, sold price: {current_price}",
                    )
        else:
            # Get last peak_period klines
            peak_line = max(klines, key=lambda x: x["high"])

            # Buy current
            if (peak_line["high"] / current_line["high"]) > peak_percentage:
                fees += fee_rate * base_currency_amount
                base_pre_sold_amount = base_currency_amount
                target_currency_amount = base_currency_amount / current_price
                base_currency_amount = 0
                selling_price = current_price * target_profit
                selling_list_time = current_time
                bought += 1
                print_log(
                    ennanble_log,
                    Fore.WHITE
                    + f"[Bought] {current_time} base: {base_currency_amount}, target: {target_currency_amount}, current price: {current_price}, selling price: {selling_price}",
                )

        current += timedelta(minutes=1)

    total_amount = base_currency_amount or base_pre_sold_amount
    print(f"Total Amount: {total_amount}")
    print(f"Fees: {fees}")
    print(Fore.GREEN + f"Final Amount: {total_amount - fees}")
    print(Fore.WHITE + f"Sold: {profit_sold}")
    print(f"Drop Sold: {drop_sold}")


simulate(datetime(2021, 4, 1), 1.04, 12, 1.02, 48)