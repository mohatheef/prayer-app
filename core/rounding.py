import math

def round_time(hours, policy="nearest"):
    if policy == "floor":
        return math.floor(hours * 60) / 60
    if policy == "ceil":
        return math.ceil(hours * 60) / 60
    return round(hours * 60) / 60
