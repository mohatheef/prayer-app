import streamlit as st
from datetime import date
from core.cities import CITIES
from core.prayer_engine import get_prayer_times
from core.csv_generator import generate_year_csv
from core.location import get_location_from_ip
from core.qibla import qibla_direction

# --------------------
# Page config
# --------------------
st.set_page_config(
    page_title="Prayer Times (Shafi · Hanafi · Umm al-Qura)",
    page_icon="🕌",
    layout="centered"
)

st.title("🕌 Prayer Times Calculator")
st.caption("Shafi & Hanafi Madhhab · Umm al-Qura · Asia/Kolkata")

# --------------------
# Session State Init
# --------------------
if "auto" not in st.session_state:
    st.session_state.auto = False
    st.session_state.lat = None
    st.session_state.lng = None
    st.session_state.city = None

# --------------------
# Sidebar
# --------------------
st.sidebar.header("Settings")

# Madhhab selector (NEW)
madhhab = st.sidebar.radio(
    "Asr Madhhab",
    ["Shafi", "Hanafi"],
    index=0
)

# Auto-detect button
if st.sidebar.button("📍 Auto-detect Location"):
    try:
        loc = get_location_from_ip()
        st.session_state.lat = loc["lat"]
        st.session_state.lng = loc["lng"]
        st.session_state.city = loc.get("city", "Detected Location")
        st.session_state.auto = True
    except Exception:
        st.sidebar.error("Auto-detect failed. Please select city manually.")

# Location selection logic
if st.session_state.auto:
    city_name = st.session_state.city
    lat = st.session_state.lat
    lng = st.session_state.lng

    st.sidebar.success(f"Detected: {city_name}")
    st.sidebar.caption(f"Lat: {lat:.4f}, Lng: {lng:.4f}")

    if st.sidebar.button("↩️ Switch to Manual City"):
        st.session_state.auto = False
else:
    city_name = st.sidebar.selectbox(
        "Select City",
        sorted(CITIES.keys())
    )
    lat = CITIES[city_name]["lat"]
    lng = CITIES[city_name]["lng"]

# Date & year
selected_date = st.sidebar.date_input(
    "Select Date",
    date.today()
)

year = st.sidebar.number_input(
    "CSV Year",
    min_value=2024,
    max_value=2100,
    value=selected_date.year
)

# --------------------
# Daily Prayer Times
# --------------------
st.subheader(f"📅 Prayer Times for {city_name}")

times = get_prayer_times(
    lat,
    lng,
    selected_date,
    madhhab=madhhab
)

col1, col2 = st.columns(2)

with col1:
    st.metric("Fajr", times["fajr"])
    st.metric("Sunrise", times["sunrise"])
    st.metric("Dhuhr", times["dhuhr"])

with col2:
    st.metric("Asr", times["asr"])
    st.metric("Maghrib", times["maghrib"])
    st.metric("Isha", times["isha"])

# --------------------
# Qibla
# --------------------
bearing = qibla_direction(lat, lng)
st.metric("🧭 Qibla Direction", f"{bearing}°")

# --------------------
# CSV Export
# --------------------
st.divider()
st.subheader("📥 Export Full-Year Prayer Calendar")

if st.button("Generate Yearly CSV"):
    filename = generate_year_csv(city_name, year, madhhab=madhhab)
    st.success("CSV generated successfully!")

    with open(filename, "rb") as f:
        st.download_button(
            "⬇️ Download CSV",
            f,
            file_name=filename,
            mime="text/csv"
        )

# --------------------
# Footer (Islamic intention + credit)
# --------------------
st.divider()
st.markdown(
    """
    <center>
    <small>
    Built by <b>Mohammed Atheef G A</b><br>
    <em>“Whoever guides someone to good will have a reward like one who did it.”</em><br>
    (Sahih Muslim)
    </small>
    </center>
    """,
    unsafe_allow_html=True
)
