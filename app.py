from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import streamlit as st

from core.cities import CITIES
from core.csv_generator import generate_year_csv
from core.hijri import gregorian_to_hijri
from core.location import get_location_from_ip
from core.masjid_offsets import MASJID_OFFSETS
from core.prayer_engine import CALCULATION_PROFILES, get_prayer_times
from core.prayer_status import get_prayer_status
from core.qibla import qibla_direction


def qibla_cardinal(deg: float) -> str:
    cards = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return cards[int((deg + 22.5) // 45) % 8]


@st.cache_data(ttl=1800)
def cached_location_lookup():
    return get_location_from_ip()


@st.cache_data(show_spinner=False)
def cached_year_csv(
    city: str,
    year: int,
    madhhab: str,
    timezone_name: str,
    method: str,
    minute_adjustment: int,
):
    return generate_year_csv(
        city=city,
        year=year,
        madhhab=madhhab,
        timezone_name=timezone_name,
        method=method,
        minute_adjustment=minute_adjustment,
    )


st.set_page_config(
    page_title="Prayer Times - Udupi",
    page_icon="🕌",
    layout="centered",
)

st.title("🕌 Prayer Times")
st.caption("India-focused prayer calendar with Udupi/Karnataka defaults")

if "auto" not in st.session_state:
    st.session_state.auto = False
    st.session_state.lat = None
    st.session_state.lng = None
    st.session_state.city = None
    st.session_state.timezone = "Asia/Kolkata"
    st.session_state.default_city = "Udupi"

st.markdown("### 📍 Quick City Switch")
quick_cities = [
    "Udupi",
    "Kundapura",
    "Manipal",
    "Mangaluru",
    "Bhatkal",
    "Bengaluru",
]
cols = st.columns(3)
for i, city in enumerate(quick_cities):
    if cols[i % 3].button(city, use_container_width=True):
        st.session_state.default_city = city
        st.session_state.auto = False
        st.session_state.timezone = "Asia/Kolkata"

st.sidebar.header("Settings")

madhhab = st.sidebar.radio("Asr Madhhab", ["Shafi", "Hanafi"], index=0)
method = st.sidebar.selectbox(
    "Calculation Method",
    list(CALCULATION_PROFILES.keys()),
    index=0,
)
minute_adjustment = st.sidebar.slider(
    "Manual Adjustment (minutes)",
    min_value=-10,
    max_value=10,
    value=0,
    step=1,
)

if st.sidebar.button("📍 Auto-detect Location"):
    try:
        loc = cached_location_lookup()
        st.session_state.lat = loc["lat"]
        st.session_state.lng = loc["lng"]
        st.session_state.city = loc.get("city", "Detected Location")
        st.session_state.timezone = loc.get("timezone", "Asia/Kolkata")
        st.session_state.auto = True
    except Exception:
        st.sidebar.error("Auto-detect failed. Please select city manually.")

if st.session_state.auto:
    city_name = st.session_state.city
    lat = float(st.session_state.lat)
    lng = float(st.session_state.lng)
    timezone_name = st.session_state.timezone or "Asia/Kolkata"
    st.sidebar.success(f"Detected: {city_name}")
    st.sidebar.caption(f"Lat: {lat:.4f}, Lng: {lng:.4f}")
    st.sidebar.caption(f"TZ: {timezone_name}")
    if st.sidebar.button("↩ Switch to Manual City"):
        st.session_state.auto = False
        st.session_state.timezone = "Asia/Kolkata"
else:
    city_keys = sorted(CITIES.keys())
    default_city = st.session_state.default_city
    default_index = city_keys.index(default_city) if default_city in city_keys else 0
    city_name = st.sidebar.selectbox("All Cities", city_keys, index=default_index)
    lat = CITIES[city_name]["lat"]
    lng = CITIES[city_name]["lng"]
    timezone_name = "Asia/Kolkata"

local_offset_label = "None (No Local Offset)"
local_offset_value = 0
if city_name in MASJID_OFFSETS:
    options = list(MASJID_OFFSETS[city_name].keys())
    local_offset_label = st.sidebar.selectbox(
        "Local Masjid Profile",
        options,
        index=0,
    )
    local_offset_value = MASJID_OFFSETS[city_name][local_offset_label]

effective_adjustment = minute_adjustment + local_offset_value

selected_date = st.sidebar.date_input("Select Date", date.today())
year = st.sidebar.number_input(
    "CSV Year",
    min_value=2024,
    max_value=2100,
    value=selected_date.year,
)

times = get_prayer_times(
    lat=lat,
    lng=lng,
    d=selected_date,
    madhhab=madhhab,
    timezone_name=timezone_name,
    method=method,
    minute_adjustment=effective_adjustment,
)

hijri = gregorian_to_hijri(selected_date)
st.subheader(f"📅 {city_name} - {selected_date.isoformat()}")
st.caption(f"Hijri: {hijri} | Method: {method} | Timezone: {timezone_name}")
if local_offset_value != 0:
    st.caption(f"Masjid profile: {local_offset_label} ({local_offset_value:+d} min)")

if selected_date == datetime.now(ZoneInfo(timezone_name)).date():
    status = get_prayer_status(datetime.now(ZoneInfo(timezone_name)), times)
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Prayer", status["current_prayer"])
    c2.metric("Next Prayer", status["next_prayer"])
    c3.metric("Starts In", status["countdown"])

col1, col2 = st.columns(2)
with col1:
    st.metric("Fajr", times["fajr"])
    st.metric("Sunrise", times["sunrise"])
    st.metric("Dhuhr", times["dhuhr"])
with col2:
    st.metric("Asr", times["asr"])
    st.metric("Maghrib", times["maghrib"])
    st.metric("Isha", times["isha"])

st.info(f"Sehri ends: {times['fajr']}  |  Iftar starts: {times['maghrib']}")

bearing = qibla_direction(lat, lng)
st.metric("🧭 Qibla Direction", f"{bearing}° ({qibla_cardinal(bearing)})")

st.divider()
st.subheader("📥 Export Full-Year Prayer Calendar")
filename, csv_bytes = cached_year_csv(
    city=city_name,
    year=int(year),
    madhhab=madhhab,
    timezone_name=timezone_name,
    method=method,
    minute_adjustment=effective_adjustment,
)
st.download_button(
    "⬇ Download CSV",
    data=csv_bytes,
    file_name=filename,
    mime="text/csv",
)

st.divider()
st.markdown(
    """
    <center>
    🐞 <a href="https://github.com/mohatheef/prayer-app/issues" target="_blank">Report an Issue</a>
    &nbsp; | &nbsp;
    👥 <a href="https://github.com/mohatheef/prayer-app/graphs/contributors" target="_blank">Contributors</a>
    </center>
    """,
    unsafe_allow_html=True,
)
