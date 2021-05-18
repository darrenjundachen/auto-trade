from re import L


from datetime import datetime
import math

def datetime_to_timestamp(datetime):
    return int(datetime.timestamp() * 1000)


def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)


def log(message):
    f = open("../log.txt", "a")
    f.write(f"[{datetime.now()}]\n{message}\n")
    f.close()

def round_decimals_down(number:float, decimals:int=2):
    """
    Returns a value rounded down to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor
