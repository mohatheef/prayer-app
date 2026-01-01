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

if "default_city" not in st.session_state:
    st.session_state.default_city = "Kundapura"

# --------------------
# MAIN PAGE – Quick City Switch (Mobile Friendly)
# --------------------
st.markdown("### 📍 Quick City Switch")

quick_cities = [
    "Kundapura",
    "Udupi",
    "Mangaluru",
    "Bengaluru",
    "Honnavar",
    "Bhatkal",
]

cols = st.columns(3)
for i, city in enumerate(quick_cities):
    if cols[i % 3].button(city, use_container_width=True):
        st.session_state.default_city = city
        st.session_state.auto = False

# --------------------
# Sidebar
# --------------------
st.sidebar.header("Settings")

madhhab = st.sidebar.radio(
    "Asr Madhhab",
    ["Shafi", "Hanafi"],
    index=0
)

# --------------------
# Auto-detect
# --------------------
if st.sidebar.button("📍 Auto-detect Location"):
    try:
        loc = get_location_from_ip()
        st.session_state.lat = loc["lat"]
        st.session_state.lng = loc["lng"]
        st.session_state.city = loc.get("city", "Detected Location")
        st.session_state.auto = True
    except Exception:
        st.sidebar.error("Auto-detect failed. Please select city manually.")

# --------------------
# Location logic
# --------------------
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
        "All Cities",
        sorted(CITIES.keys()),
        index=sorted(CITIES.keys()).index(st.session_state.default_city)
    )
    lat = CITIES[city_name]["lat"]
    lng = CITIES[city_name]["lng"]

# --------------------
# Date & year
# --------------------
selected_date = st.sidebar.date_input("Select Date", date.today())

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

times = get_prayer_times(lat, lng, selected_date, madhhab=madhhab)

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
        st.download_button("⬇️ Download CSV", f, file_name=filename)

# --------------------
# Community & Footer
# --------------------
st.divider()

st.markdown(
    """
    <center>
    🐞 <a href="https://github.com/mohatheef/prayer-app/issues" target="_blank">Report an Issue</a>
    &nbsp; | &nbsp;
    📝 <a href="https://forms.gle/nhoVNjB5SN2a32Lq8" target="_blank">Send Feedback</a>
    &nbsp; | &nbsp;
    👥 <a href="https://github.com/mohatheef/prayer-app/graphs/contributors" target="_blank">Contributors</a>
    </center>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <center>
    <small>
    Built by <b>Mohammed Atheef G A</b><br>
    <em>“Whoever guides someone to good will have a reward like one who did it.”</em><br>
    (Sahih Muslim)<br><br>
    💻 <a href="https://github.com/mohatheef/prayer-app" target="_blank">Open Source (MIT License)</a><br>
    📩 <a href="mailto:atheefga18@gmail.com">atheefga18@gmail.com</a>
    </small>
    </center>
    """,
    unsafe_allow_html=True
)
