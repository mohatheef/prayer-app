# Prayer App (India / Udupi Focus)

A Netlify-native prayer-times web app tuned for Karnataka coastal usage.

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
cd web
python3 -m http.server 8080
```

## Deploy

### Netlify

This repo is now configured as a native Netlify static app.

- `netlify.toml` publishes the `web/` folder.
- Prayer calculations run fully in browser JavaScript.
- No Streamlit/Render runtime needed for Netlify hosting.

## Notes

- For India, timezone is usually `Asia/Kolkata`.
- If local masjid times differ by a few minutes, use `Manual Adjustment`.
- If your masjid has a stable offset, use `Local Masjid Profile` first, then add fine tuning via `Manual Adjustment`.
- Calculations are astronomical estimates; follow your local masjid timetable when needed.
