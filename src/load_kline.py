from binance_api import *
from datetime import datetime
import pymongo
from utils import timestamp_to_datetime

client = pymongo.MongoClient("localhost", 27017)
db = client.trade

if db.klines.find_one():
    from_date = db.klines.find().sort("open_time", -1)[0]["close_time"]
else:
    from_date = datetime(2020, 5, 17)

to_date = datetime.now()

while True:
    klines = get_klines(from_date, to_date)

    if not klines:
        break

    db.klines.insert_many(
        [
            {
                "open_time": kline[0],
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
                "close_time": kline[6],
                "quote_asset_volume": float(kline[7]),
                "number_of_trades": float(kline[8]),
                "taker_buy_base_asset_volume": float(kline[9]),
                "taker_buy_quote_asset_volume": float(kline[10]),
                "ignore": float(kline[11]),
            }
            for kline in klines
        ]
    )

    from_date = klines[-1][6]
    print(timestamp_to_datetime(klines[-1][0]))
