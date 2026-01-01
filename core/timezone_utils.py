
import pytz
from datetime import datetime, timedelta

def apply_timezone(decimal_hours, tz_name, date):
    tz = pytz.timezone(tz_name)
    hours = int(decimal_hours)
    minutes = int((decimal_hours - hours) * 60)

    dt = datetime(
        date.year, date.month, date.day,
        hours, minutes
    )

    localized = tz.localize(dt)
    return localized.strftime("%H:%M")
