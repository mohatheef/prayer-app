# Prayer App (India / Udupi Focus)

A modern Streamlit prayer-times app tuned for Karnataka coastal usage.

## Highlights

- Udupi default city and fast city switching
- Shafi and Hanafi Asr modes
- Calculation profiles:
  - Karnataka Coast (Fajr/Isha at -18°)
  - Umm al-Qura (Fajr -18.5°, Isha +90 min after Maghrib)
- Auto location detect with timezone support
- Current prayer, next prayer, and countdown
- Sehri end and Iftar start shortcuts
- Qibla direction with bearing + cardinal direction
- Local masjid profile offsets for Udupi/Kundapura/Mangaluru
- Full-year CSV export in memory (cloud-friendly)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

### Render (recommended)

1. Push this repository to GitHub.
2. Create a new Render web service from the repo.
3. Render auto-detects `render.yaml`.
4. Deploy.

### Streamlit Community Cloud

1. Connect GitHub repo in Streamlit Cloud.
2. App file path: `app.py`
3. Deploy.

### Netlify

Netlify is configured as a landing/redirect site in this repo.

- `netlify.toml` redirects all routes to:
  - `https://salahtime.streamlit.app`
- `netlify/index.html` provides fallback manual click redirect.

If your app URL changes, update both files with the new URL.

## Notes

- For India, timezone is usually `Asia/Kolkata`.
- If local masjid times differ by a few minutes, use `Manual Adjustment`.
- If your masjid has a stable offset, use `Local Masjid Profile` first, then add fine tuning via `Manual Adjustment`.
- Calculations are astronomical estimates; follow your local masjid timetable when needed.
