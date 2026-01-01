import math

DEG2RAD = math.pi / 180
RAD2DEG = 180 / math.pi

def julian_day(year, month, day):
    if month <= 2:
        year -= 1
        month += 12

    A = year // 100
    B = 2 - A + A // 4

    jd = int(365.25 * (year + 4716)) \
       + int(30.6001 * (month + 1)) \
       + day + B - 1524.5

    return jd


def solar_declination(jd):
    n = jd - 2451545.0
    g = (357.529 + 0.98560028 * n) * DEG2RAD
    q = (280.459 + 0.98564736 * n) * DEG2RAD
    L = q + (1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) * DEG2RAD

    return math.asin(math.sin(L) * math.sin(23.439 * DEG2RAD))


def equation_of_time(jd):
    n = jd - 2451545.0
    g = (357.529 + 0.98560028 * n) * DEG2RAD
    q = (280.459 + 0.98564736 * n) * DEG2RAD
    L = q + (1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) * DEG2RAD

    e = 0.016708
    E = (
        -1.915 * math.sin(g)
        - 0.020 * math.sin(2 * g)
        + 2.466 * math.sin(2 * L)
        - 0.053 * math.sin(4 * L)
    )

    return E  # minutes
