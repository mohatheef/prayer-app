const CITIES = {
  Udupi: { lat: 13.3409, lng: 74.7421 },
  Kundapura: { lat: 13.633, lng: 74.69 },
  Manipal: { lat: 13.352, lng: 74.792 },
  Mangaluru: { lat: 12.9141, lng: 74.856 },
  Bhatkal: { lat: 13.985, lng: 74.555 },
  Bengaluru: { lat: 12.9716, lng: 77.5946 },
  Karwar: { lat: 14.8136, lng: 74.1297 },
  Honnavar: { lat: 14.28, lng: 74.44 },
  Kochi: { lat: 9.9312, lng: 76.2673 },
  Mumbai: { lat: 19.076, lng: 72.8777 },
  Delhi: { lat: 28.6139, lng: 77.209 },
};

const MASJID_OFFSETS = {
  Udupi: {
    "None (No Local Offset)": 0,
    "Jumma Masjid Udupi (Typical)": 2,
    "Town Masjid (Typical)": 3,
  },
  Kundapura: {
    "None (No Local Offset)": 0,
    "Jamia Masjid Kundapura (Typical)": 2,
  },
  Mangaluru: {
    "None (No Local Offset)": 0,
    "Central Masjid Mangaluru (Typical)": 2,
  },
};

const METHODS = {
  "Karnataka Coast": { fajrAngle: -18.0, ishaAngle: -18.0, ishaIntervalMin: null },
  "Umm al-Qura": { fajrAngle: -18.5, ishaAngle: null, ishaIntervalMin: 90 },
};

const PRAYER_KEYS = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"];
const KAABA = { lat: 21.4225, lng: 39.8262 };

const citySelect = document.getElementById("citySelect");
const dateInput = document.getElementById("dateInput");
const madhhabSelect = document.getElementById("madhhabSelect");
const methodSelect = document.getElementById("methodSelect");
const adjustInput = document.getElementById("adjustInput");
const masjidSelect = document.getElementById("masjidSelect");
const detectBtn = document.getElementById("detectBtn");
const downloadBtn = document.getElementById("downloadBtn");
const metaLine = document.getElementById("metaLine");
const sehriLine = document.getElementById("sehriLine");
const timingGrid = document.getElementById("timingGrid");
const qiblaText = document.getElementById("qiblaText");
const currentPrayer = document.getElementById("currentPrayer");
const nextPrayer = document.getElementById("nextPrayer");
const countdown = document.getElementById("countdown");

let geoOverride = null;

function deg2rad(d) {
  return (d * Math.PI) / 180;
}

function rad2deg(r) {
  return (r * 180) / Math.PI;
}

function julianDay(y, m, day) {
  let yy = y;
  let mm = m;
  if (mm <= 2) {
    yy -= 1;
    mm += 12;
  }
  const A = Math.floor(yy / 100);
  const B = 2 - A + Math.floor(A / 4);
  return Math.floor(365.25 * (yy + 4716)) + Math.floor(30.6001 * (mm + 1)) + day + B - 1524.5;
}

function solarDeclination(jd) {
  const n = jd - 2451545.0;
  const g = deg2rad(357.529 + 0.98560028 * n);
  const q = deg2rad(280.459 + 0.98564736 * n);
  const L = q + deg2rad(1.915 * Math.sin(g) + 0.02 * Math.sin(2 * g));
  return Math.asin(Math.sin(L) * Math.sin(deg2rad(23.439)));
}

function equationOfTime(jd) {
  const n = jd - 2451545.0;
  const g = deg2rad(357.529 + 0.98560028 * n);
  const q = deg2rad(280.459 + 0.98564736 * n);
  const L = q + deg2rad(1.915 * Math.sin(g) + 0.02 * Math.sin(2 * g));
  return (
    -1.915 * Math.sin(g) -
    0.02 * Math.sin(2 * g) +
    2.466 * Math.sin(2 * L) -
    0.053 * Math.sin(4 * L)
  );
}

function hourAngle(lat, decl, altitude) {
  const latRad = deg2rad(lat);
  const altRad = deg2rad(altitude);
  let cosH =
    (Math.sin(altRad) - Math.sin(latRad) * Math.sin(decl)) /
    (Math.cos(latRad) * Math.cos(decl));
  cosH = Math.max(-1, Math.min(1, cosH));
  return rad2deg(Math.acos(cosH)) / 15;
}

function asrAltitude(lat, decl, shadowRatio) {
  const latRad = deg2rad(lat);
  const z = Math.atan(shadowRatio + Math.abs(Math.tan(latRad - decl)));
  return rad2deg(Math.PI / 2 - z);
}

function toHHMM(hoursFloat) {
  const total = ((Math.round(hoursFloat * 60) % 1440) + 1440) % 1440;
  const h = Math.floor(total / 60);
  const m = total % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

function parseDateInput(value) {
  const [y, m, d] = value.split("-").map(Number);
  return { y, m, d };
}

function getTimezoneOffsetHours(dateObj) {
  const jan = new Date(dateObj.getFullYear(), 0, 1).getTimezoneOffset();
  const now = dateObj.getTimezoneOffset();
  const offset = now === jan ? now : now;
  return -offset / 60;
}

function getPrayerTimes(lat, lng, dateValue, madhhab, method, adjustmentMin) {
  const { y, m, d } = parseDateInput(dateValue);
  const jd = julianDay(y, m, d);
  const decl = solarDeclination(jd);
  const eot = equationOfTime(jd);
  const tzOffset = getTimezoneOffsetHours(new Date(y, m - 1, d));
  const solarNoon = 12 + tzOffset - lng / 15 - eot / 60;
  const profile = METHODS[method];
  const sunAlt = -0.833;
  const shadow = madhhab === "Hanafi" ? 2 : 1;
  const adj = adjustmentMin / 60;

  const fajr = solarNoon - hourAngle(lat, decl, profile.fajrAngle);
  const sunrise = solarNoon - hourAngle(lat, decl, sunAlt);
  const dhuhr = solarNoon;
  const asr = solarNoon + hourAngle(lat, decl, asrAltitude(lat, decl, shadow));
  const maghrib = solarNoon + hourAngle(lat, decl, sunAlt);
  const isha =
    profile.ishaIntervalMin != null
      ? maghrib + profile.ishaIntervalMin / 60
      : solarNoon + hourAngle(lat, decl, profile.ishaAngle);

  return {
    fajr: toHHMM(fajr + adj),
    sunrise: toHHMM(sunrise + adj),
    dhuhr: toHHMM(dhuhr + adj),
    asr: toHHMM(asr + adj),
    maghrib: toHHMM(maghrib + adj),
    isha: toHHMM(isha + adj),
  };
}

function qiblaDirection(lat, lng) {
  const latR = deg2rad(lat);
  const lngR = deg2rad(lng);
  const kaabaLat = deg2rad(KAABA.lat);
  const kaabaLng = deg2rad(KAABA.lng);
  const dLng = kaabaLng - lngR;
  const angle = Math.atan2(
    Math.sin(dLng),
    Math.cos(latR) * Math.tan(kaabaLat) - Math.sin(latR) * Math.cos(dLng)
  );
  const bearing = (rad2deg(angle) + 360) % 360;
  const dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
  return `${bearing.toFixed(2)}° (${dirs[Math.floor((bearing + 22.5) / 45) % 8]})`;
}

function toDateTime(baseDate, hhmm) {
  const [h, m] = hhmm.split(":").map(Number);
  const dt = new Date(baseDate);
  dt.setHours(h, m, 0, 0);
  return dt;
}

function prayerStatus(baseDate, times) {
  const schedule = PRAYER_KEYS.map((k) => [k, toDateTime(baseDate, times[k])]);
  let current = schedule[schedule.length - 1];
  let next = [schedule[0][0], new Date(schedule[0][1].getTime() + 24 * 3600 * 1000)];
  for (let i = 0; i < schedule.length; i += 1) {
    if (baseDate >= schedule[i][1]) {
      current = schedule[i];
      if (i < schedule.length - 1) {
        next = schedule[i + 1];
      }
    } else {
      break;
    }
  }
  const diff = Math.max(0, Math.floor((next[1] - baseDate) / 1000));
  const hh = String(Math.floor(diff / 3600)).padStart(2, "0");
  const mm = String(Math.floor((diff % 3600) / 60)).padStart(2, "0");
  return {
    current: current[0],
    next: next[0],
    countdown: `${hh}h ${mm}m`,
  };
}

function hijriForDate(dateObj) {
  try {
    return new Intl.DateTimeFormat("en-TN-u-ca-islamic", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }).format(dateObj);
  } catch (e) {
    return "Hijri unavailable";
  }
}

function buildMasjidOptions(city) {
  const map = MASJID_OFFSETS[city] || { "None (No Local Offset)": 0 };
  masjidSelect.innerHTML = "";
  Object.keys(map).forEach((label) => {
    const option = document.createElement("option");
    option.value = label;
    option.textContent = label;
    masjidSelect.appendChild(option);
  });
}

function renderTimes(times) {
  timingGrid.innerHTML = "";
  PRAYER_KEYS.forEach((key) => {
    const card = document.createElement("div");
    card.className = "timing-card";
    const name = document.createElement("h4");
    name.textContent = key.charAt(0).toUpperCase() + key.slice(1);
    const value = document.createElement("p");
    value.textContent = times[key];
    card.appendChild(name);
    card.appendChild(value);
    timingGrid.appendChild(card);
  });
}

function selectedCoords() {
  if (geoOverride) return geoOverride;
  return CITIES[citySelect.value];
}

function refresh() {
  const city = citySelect.value;
  const coords = selectedCoords();
  const method = methodSelect.value;
  const madhhab = madhhabSelect.value;
  const manual = Number(adjustInput.value || 0);
  const masjidMap = MASJID_OFFSETS[city] || { "None (No Local Offset)": 0 };
  const masjid = masjidSelect.value || "None (No Local Offset)";
  const localOffset = masjidMap[masjid] || 0;
  const totalAdj = manual + localOffset;
  const dateVal = dateInput.value;
  const dt = new Date(`${dateVal}T00:00:00`);
  const times = getPrayerTimes(coords.lat, coords.lng, dateVal, madhhab, method, totalAdj);

  metaLine.textContent = `${city} | Hijri: ${hijriForDate(dt)} | Method: ${method} | Offset: ${totalAdj >= 0 ? "+" : ""}${totalAdj} min`;
  sehriLine.textContent = `Sehri ends: ${times.fajr} | Iftar starts: ${times.maghrib}`;
  qiblaText.textContent = qiblaDirection(coords.lat, coords.lng);
  renderTimes(times);

  const now = new Date();
  const isToday = now.toDateString() === dt.toDateString();
  if (isToday) {
    const status = prayerStatus(now, times);
    currentPrayer.textContent = status.current.toUpperCase();
    nextPrayer.textContent = status.next.toUpperCase();
    countdown.textContent = status.countdown;
  } else {
    currentPrayer.textContent = "-";
    nextPrayer.textContent = "-";
    countdown.textContent = "-";
  }
}

function downloadCsv() {
  const city = citySelect.value;
  const coords = selectedCoords();
  const year = new Date(dateInput.value).getFullYear();
  const method = methodSelect.value;
  const madhhab = madhhabSelect.value;
  const manual = Number(adjustInput.value || 0);
  const masjidMap = MASJID_OFFSETS[city] || { "None (No Local Offset)": 0 };
  const masjid = masjidSelect.value || "None (No Local Offset)";
  const localOffset = masjidMap[masjid] || 0;
  const totalAdj = manual + localOffset;
  const rows = [
    [
      "city",
      "date_gregorian",
      "date_hijri",
      "madhhab",
      "method",
      "minute_adjustment",
      "fajr",
      "sunrise",
      "dhuhr",
      "asr",
      "maghrib",
      "isha",
    ],
  ];

  for (let i = 0; i < 366; i += 1) {
    const d = new Date(year, 0, 1 + i);
    if (d.getFullYear() !== year) break;
    const dateValue = d.toISOString().slice(0, 10);
    const times = getPrayerTimes(coords.lat, coords.lng, dateValue, madhhab, method, totalAdj);
    rows.push([
      city,
      dateValue,
      hijriForDate(d),
      madhhab,
      method,
      String(totalAdj),
      times.fajr,
      times.sunrise,
      times.dhuhr,
      times.asr,
      times.maghrib,
      times.isha,
    ]);
  }

  const csvText = rows.map((r) => r.join(",")).join("\n");
  const blob = new Blob([csvText], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const safeMethod = method.replace(/\s+/g, "");
  a.href = url;
  a.download = `${city}_${year}_${madhhab}_${safeMethod}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function init() {
  Object.keys(CITIES)
    .sort()
    .forEach((city) => {
      const option = document.createElement("option");
      option.value = city;
      option.textContent = city;
      citySelect.appendChild(option);
    });
  citySelect.value = "Udupi";
  buildMasjidOptions("Udupi");

  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, "0");
  const dd = String(today.getDate()).padStart(2, "0");
  dateInput.value = `${yyyy}-${mm}-${dd}`;

  [citySelect, dateInput, madhhabSelect, methodSelect, adjustInput, masjidSelect].forEach((el) => {
    el.addEventListener("change", () => {
      if (el === citySelect) {
        geoOverride = null;
        buildMasjidOptions(citySelect.value);
      }
      refresh();
    });
  });

  detectBtn.addEventListener("click", () => {
    if (!navigator.geolocation) {
      alert("Geolocation not supported in this browser.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        geoOverride = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        refresh();
      },
      () => alert("Could not fetch location. Please allow location permission.")
    );
  });

  downloadBtn.addEventListener("click", downloadCsv);
  setInterval(refresh, 60000);
  refresh();
}

init();
