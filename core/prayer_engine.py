from datetime import date
from .astro_utils import julian_day, solar_declination, equation_of_time
from .solar_angles import hour_angle, asr_altitude

TZ_OFFSET = 5.5  # Asia/Kolkata
FAJR_ANGLE = -18.5
SUN_ALT = -0.833


def to_hhmm(hours):
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h:02d}:{m:02d}"


def get_prayer_times(
    lat: float,
    lng: float,
    d: date,
    madhhab: str = "Shafi"
):
    """
    Core prayer-time engine
    - Calculation: Umm al-Qura
    - Asr: Shafi or Hanafi (shadow-based)
    - Timezone: Asia/Kolkata
    """

    jd = julian_day(d.year, d.month, d.day)
    decl = solar_declination(jd)
    eot = equation_of_time(jd)

    solar_noon = 12 + TZ_OFFSET - (lng / 15) - (eot / 60)

    fajr = solar_noon - hour_angle(lat, decl, FAJR_ANGLE)
    sunrise = solar_noon - hour_angle(lat, decl, SUN_ALT)
    dhuhr = solar_noon

    # ---- Asr (madhhab-based) ----
    shadow_ratio = 2 if madhhab == "Hanafi" else 1
    asr = solar_noon + hour_angle(
        lat,
        decl,
        asr_altitude(lat, decl, shadow_ratio)
    )

    maghrib = solar_noon + hour_angle(lat, decl, SUN_ALT)
    isha = maghrib + 1.5  # Umm al-Qura (90 min)

    return {
        "fajr": to_hhmm(fajr),
        "sunrise": to_hhmm(sunrise),
        "dhuhr": to_hhmm(dhuhr),
        "asr": to_hhmm(asr),
        "maghrib": to_hhmm(maghrib),
        "isha": to_hhmm(isha),
    }
