from datetime import date
from core.prayer_engine import get_prayer_times
from core.cities import CITIES

city = "Udupi"
coords = CITIES[city]

times = get_prayer_times(
    coords["lat"],
    coords["lng"],
    date.today()
)

print(f"\n🕌 Prayer Times – {city}\n")
for k, v in times.items():
    print(f"{k.capitalize():8s}: {v}")
