from trade import get_current_selling_price, get_current_buying_price, sell_all, buy_all
import sys
import time

if len(sys.argv) == 2:
    op = sys.argv[1]
    if op == "sell_all":
        while True:
            current_buying_price = get_current_buying_price()
            if sell_all(current_buying_price):
                print(f"Sold with price {current_buying_price}")
                break
            print(f"Failed to sell with price {current_buying_price}")
            time.sleep(1)
    elif op == "buy_all":
        while True:
            current_selling_price = get_current_selling_price()
            if buy_all(current_selling_price):
                print(f"Bought with price {current_selling_price}")
                break
            print(f"Failed to buy with price {current_selling_price}")
            time.sleep(1)

    else:
        raise Exception("Either sell_all or buy_all")
else:
    raise Exception("Nah")
