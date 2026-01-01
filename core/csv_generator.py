import csv
from datetime import date, timedelta
from .prayer_engine import get_prayer_times
from .cities import CITIES
from .hijri import gregorian_to_hijri

TZ_NAME = "Asia/Kolkata"


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def generate_year_csv(city: str, year: int):
    if city not in CITIES:
        raise ValueError("City not found")

    coords = CITIES[city]
    days = 366 if is_leap_year(year) else 365
    start = date(year, 1, 1)

    filename = f"{city}_{year}_Shafi_UmmAlQura.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # ---- Header ----
        writer.writerow([
            "city",
            "date_gregorian",
            "date_hijri",
            "timezone",
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
                d
            )

            writer.writerow([
                city,
                d.isoformat(),
                gregorian_to_hijri(d),
                TZ_NAME,
                times["fajr"],
                times["sunrise"],
                times["dhuhr"],
                times["asr"],
                times["maghrib"],
                times["isha"],
            ])

    return filename
