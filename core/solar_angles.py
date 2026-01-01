import math
from .astro_utils import DEG2RAD, RAD2DEG

def hour_angle(lat, decl, altitude):
    lat *= DEG2RAD
    altitude *= DEG2RAD

    cos_h = (
        math.sin(altitude)
        - math.sin(lat) * math.sin(decl)
    ) / (
        math.cos(lat) * math.cos(decl)
    )

    return math.acos(cos_h) * RAD2DEG / 15  # hours


def asr_altitude(lat, decl):
    lat *= DEG2RAD
    angle = math.atan(1 + abs(math.tan(lat - decl)))
    return -RAD2DEG * angle
