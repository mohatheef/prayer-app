from __future__ import annotations

from datetime import datetime, timedelta

from .prayer_engine import prayer_timeline


def _parse_today_time(now: datetime, hhmm: str) -> datetime:
    hour, minute = [int(x) for x in hhmm.split(":")]
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)


def get_prayer_status(now: datetime, times: dict[str, str]) -> dict[str, str]:
    ordered = list(prayer_timeline())
    schedule = [(name, _parse_today_time(now, times[name])) for name in ordered]

    active_name = ordered[-1]
    next_name = ordered[0]
    next_time = schedule[0][1] + timedelta(days=1)

    for idx, (name, at_time) in enumerate(schedule):
        if now >= at_time:
            active_name = name
            if idx + 1 < len(schedule):
                next_name, next_time = schedule[idx + 1]
            else:
                next_name, next_time = ordered[0], schedule[0][1] + timedelta(days=1)
        else:
            break

    remaining = next_time - now
    total_seconds = max(0, int(remaining.total_seconds()))
    hrs = total_seconds // 3600
    mins = (total_seconds % 3600) // 60

    return {
        "current_prayer": active_name.capitalize(),
        "next_prayer": next_name.capitalize(),
        "next_at": next_time.strftime("%H:%M"),
        "countdown": f"{hrs:02d}h {mins:02d}m",
    }
