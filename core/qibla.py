import math

KAABA_LAT = math.radians(21.4225)
KAABA_LNG = math.radians(39.8262)

def qibla_direction(lat, lng):
    lat = math.radians(lat)
    lng = math.radians(lng)

    d_lng = KAABA_LNG - lng

    angle = math.atan2(
        math.sin(d_lng),
        math.cos(lat) * math.tan(KAABA_LAT) -
        math.sin(lat) * math.cos(d_lng)
    )

    bearing = (math.degrees(angle) + 360) % 360
    return round(bearing, 2)
