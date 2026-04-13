import csv
import io
from datetime import date, timedelta

from .prayer_engine import get_prayer_times
from .cities import CITIES
from .hijri import gregorian_to_hijri


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def generate_year_csv(
    city: str,
    year: int,
    madhhab: str = "Shafi",
    timezone_name: str = "Asia/Kolkata",
    method: str = "Karnataka Coast",
    minute_adjustment: int = 0,
):
    """
    Generate full-year prayer calendar CSV
    Supports Shafi & Hanafi Asr
    """

    if city not in CITIES:
        raise ValueError("City not found")

    coords = CITIES[city]
    days = 366 if is_leap_year(year) else 365
    start = date(year, 1, 1)

    method_safe = method.replace(" ", "")
    filename = f"{city}_{year}_{madhhab}_{method_safe}.csv"
    output = io.StringIO()
    writer = csv.writer(output)

    # ---- Header ----
    writer.writerow([
        "city",
        "date_gregorian",
        "date_hijri",
        "timezone",
        "madhhab",
        "method",
        "minute_adjustment",
        "fajr",
        "sunrise",
        "dhuhr",
        "asr",
        "maghrib",
        "isha",
    ])

    # ---- Daily rows ----
    for i in range(days):
        d = start + timedelta(days=i)

        times = get_prayer_times(
            coords["lat"],
            coords["lng"],
            d,
            madhhab=madhhab,
            timezone_name=timezone_name,
            method=method,
            minute_adjustment=minute_adjustment,
        )

        writer.writerow([
            city,
            d.isoformat(),
            gregorian_to_hijri(d),
            timezone_name,
            madhhab,
            method,
            minute_adjustment,
            times["fajr"],
            times["sunrise"],
            times["dhuhr"],
            times["asr"],
            times["maghrib"],
            times["isha"],
        ])

    return filename, output.getvalue().encode("utf-8")
