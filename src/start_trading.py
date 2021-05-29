from trade import trade, Status
from datetime import datetime
import sys

status = Status.WAITING_BUYING
sell_point_price = None
holding_highest_price = None # This is to prevent sudden spike

if len(sys.argv) == 2:
    holding_highest_price = float(sys.argv[1])
elif len(sys.argv) == 4:
    holding_highest_price = float(sys.argv[1])
    status = Status[sys.argv[2]]
    sell_point_price = float(sys.argv[3])
else:
    raise Exception("Wrong!")

assert holding_highest_price is not None
assert holding_highest_price > 20000 and holding_highest_price < 70000

trade(
    holding_highest_price=holding_highest_price,
    status=status,
    sell_point_price=sell_point_price,
)
