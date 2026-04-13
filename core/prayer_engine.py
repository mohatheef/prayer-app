from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from .astro_utils import julian_day, solar_declination, equation_of_time
from .solar_angles import hour_angle, asr_altitude


@dataclass(frozen=True)
class CalculationProfile:
    name: str
    fajr_angle: float
    isha_angle: float | None = None
    isha_interval_min: int | None = None


CALCULATION_PROFILES: dict[str, CalculationProfile] = {
    "Karnataka Coast": CalculationProfile(
        name="Karnataka Coast",
        fajr_angle=-18.0,
        isha_angle=-18.0,
    ),
    "Umm al-Qura": CalculationProfile(
        name="Umm al-Qura",
        fajr_angle=-18.5,
        isha_interval_min=90,
    ),
}

SUN_ALT = -0.833


def _timezone_offset_hours(d: date, tz_name: str) -> float:
    try:
        dt = datetime.combine(d, time(12, 0), tzinfo=ZoneInfo(tz_name))
        offset = dt.utcoffset()
    except Exception:
        return 5.5
    if offset is None:
        return 5.5
    return offset.total_seconds() / 3600.0

def to_hhmm(hours):
    total_minutes = int(round(hours * 60)) % (24 * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}"


def _resolve_profile(method: str) -> CalculationProfile:
    return CALCULATION_PROFILES.get(method, CALCULATION_PROFILES["Karnataka Coast"])


def get_prayer_times(
    lat: float,
    lng: float,
    d: date,
    madhhab: str = "Shafi",
    timezone_name: str = "Asia/Kolkata",
    method: str = "Karnataka Coast",
    minute_adjustment: int = 0,
):
    """
    Core prayer-time engine
    - Calculation profile: Karnataka Coast (default) or Umm al-Qura
    - Asr: Shafi or Hanafi (shadow-based)
    - Timezone: caller-provided (defaults to Asia/Kolkata)
    """
    profile = _resolve_profile(method)

    jd = julian_day(d.year, d.month, d.day)
    decl = solar_declination(jd)
    eot = equation_of_time(jd)
    tz_offset = _timezone_offset_hours(d, timezone_name)

    solar_noon = 12 + tz_offset - (lng / 15) - (eot / 60)

    fajr = solar_noon - hour_angle(lat, decl, profile.fajr_angle)
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
    if profile.isha_interval_min is not None:
        isha = maghrib + (profile.isha_interval_min / 60)
    else:
        isha = solar_noon + hour_angle(lat, decl, profile.isha_angle or -18.0)

    adjustment_h = minute_adjustment / 60.0

    return {
        "fajr": to_hhmm(fajr + adjustment_h),
        "sunrise": to_hhmm(sunrise + adjustment_h),
        "dhuhr": to_hhmm(dhuhr + adjustment_h),
        "asr": to_hhmm(asr + adjustment_h),
        "maghrib": to_hhmm(maghrib + adjustment_h),
        "isha": to_hhmm(isha + adjustment_h),
    }


def prayer_timeline():
    return ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha")
