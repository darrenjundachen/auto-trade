from re import L


from datetime import datetime


def datetime_to_timestamp(datetime):
    return int(datetime.timestamp() * 1000)


def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)