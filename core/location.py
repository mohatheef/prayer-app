import requests


def get_location_from_ip():
    """
    Resolve location from public IP with fallback providers.
    """
    providers = (
        "http://ip-api.com/json/",
        "https://ipapi.co/json/",
    )

    for url in providers:
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
        except Exception:
            continue

        if data.get("status") == "success":
            return {
                "city": data.get("city", "Detected Location"),
                "lat": float(data["lat"]),
                "lng": float(data["lon"]),
                "timezone": data.get("timezone", "Asia/Kolkata"),
            }

        if "latitude" in data and "longitude" in data:
            return {
                "city": data.get("city", "Detected Location"),
                "lat": float(data["latitude"]),
                "lng": float(data["longitude"]),
                "timezone": data.get("timezone", "Asia/Kolkata"),
            }

    raise RuntimeError("IP location lookup failed")
