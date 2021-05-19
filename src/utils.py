from datetime import datetime
import math

sample_log_count = {}


def datetime_to_timestamp(datetime):
    return int(datetime.timestamp() * 1000)


def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)


def log(message):
    message = f"[{datetime.now()}]\n{message}"
    file_name = datetime.now().strftime("%Y-%m-%d")
    print(message)
    f = open(f"../logs/{file_name}.txt", "a")
    f.write(message + "\n")
    f.close()


def sample_log(message, key, rate=60):
    global sample_log_count

    if not sample_log_count.get(key):
        sample_log_count[key] = 0

    file_name = datetime.now().strftime("%Y-%m-%d")
    if sample_log_count[key] % rate == 0:
        f = open(f"../logs/{file_name}.txt", "a")
        f.write(f"[{datetime.now()}]\n{message}\n")
        f.close()

    sample_log_count[key] += 1


def round_decimals_down(number: float, decimals: int = 2):
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
