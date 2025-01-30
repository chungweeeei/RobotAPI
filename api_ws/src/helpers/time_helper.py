import pytz
import datetime

def to_taipei_time(timestamp: float) -> datetime.datetime:

    time = datetime.datetime.fromtimestamp(timestamp=timestamp,
                                           tz=pytz.timezone("Asia/Taipei"))
    
    return time