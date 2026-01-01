import math
from .astro_utils import DEG2RAD, RAD2DEG

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


def asr_altitude(lat, decl):
    """
    Shafi Asr: shadow length = 1 × object height
    """
    lat_rad = lat * DEG2RAD

    angle = math.atan(
        1 / (1 + abs(math.tan(lat_rad - decl)))
    )

    return -math.degrees(angle)
