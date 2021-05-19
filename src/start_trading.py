from trade import trade, Status
from datetime import datetime
import sys

status = Status.WAITING_BUYING
sell_point_price = None
drop_time = None

if len(sys.argv) == 4:
    status = Status[sys.argv[1]]
    sell_point_price = float(sys.argv[2])
    drop_time = datetime.strptime(sys.argv[3], "%Y-%m-%d %H:%M:%S")

trade(status=status, sell_point_price=sell_point_price, drop_time=drop_time)
