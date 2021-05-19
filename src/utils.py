from datetime import datetime, timedelta
import math
import requests

sample_log_count = {}


def datetime_to_timestamp(datetime):
    return int(datetime.timestamp() * 1000)


def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)


def log(message, print_message=True):
    message = f"[{datetime.now()}]\n{message}"
    file_name = datetime.now().strftime("%Y-%m-%d")
    if print_message:
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


def message_slack(message):
    requests.post(
        "https://hooks.slack.com/services/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",
        headers={"Content-type": "application/json"},
        json={"text": message},
    )


last_sent = None


def send_heart_beat(status):
    global last_sent

    if last_sent and (last_sent + timedelta(minutes=60)) > datetime.now():
        return

    last_sent = datetime.now()

    message_slack(f"Hey, current status: {status.name}")
