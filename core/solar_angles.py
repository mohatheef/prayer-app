import math
from .astro_utils import DEG2RAD

def hour_angle(lat, decl, altitude):
    lat_rad = lat * DEG2RAD
    alt_rad = altitude * DEG2RAD

    cos_h = (
        math.sin(alt_rad)
        - math.sin(lat_rad) * math.sin(decl)
    ) / (
        math.cos(lat_rad) * math.cos(decl)
    )

    # numerical safety
    cos_h = max(-1.0, min(1.0, cos_h))

    return math.degrees(math.acos(cos_h)) / 15  # hours


def asr_altitude(lat, decl, shadow_ratio=1):
    """
    Asr altitude for given shadow ratio
    shadow_ratio = 1 → Shafi
    shadow_ratio = 2 → Hanafi
    """

    lat_rad = lat * DEG2RAD

    Z = math.atan(
        shadow_ratio + abs(math.tan(lat_rad - decl))
    )

    altitude = math.pi / 2 - Z  # 90° - zenith angle
    return math.degrees(altitude)
