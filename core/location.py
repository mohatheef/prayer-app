import requests

def get_location_from_ip():
    """
    Uses ip-api.com (more reliable for lat/lon)
    """
    url = "http://ip-api.com/json/"
    r = requests.get(url, timeout=5)
    data = r.json()

    if data.get("status") != "success":
        raise RuntimeError("IP location lookup failed")

    return {
        "city": data.get("city", "Detected Location"),
        "lat": float(data["lat"]),
        "lng": float(data["lon"]),
        "timezone": data.get("timezone", "Asia/Kolkata"),
    }
