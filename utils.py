from datetime import datetime, timedelta

def utc_to_fr_time(utc_timestamp_ms):
    utc_dt = datetime.utcfromtimestamp(utc_timestamp_ms / 1000)
    fr_dt = utc_dt + timedelta(hours=1)
    return fr_dt.strftime("%Y-%m-%d %H:%M")