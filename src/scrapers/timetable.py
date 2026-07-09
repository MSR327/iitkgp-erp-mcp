import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from ..auth.login import get_session

TIMETABLE_URL = "https://erp.iitkgp.ac.in/Academic/timetable_student.htm"

SLOT_TIMINGS = {
    "A": "08:00-08:55",
    "B": "09:00-09:55",
    "C": "10:00-10:55",
    "D": "11:00-11:55",
    "E": "12:00-12:55",
    "F": "14:00-14:55",
    "G": "15:00-15:55",
    "H": "16:00-16:55",
    "I": "17:00-17:55",
    "J": "18:00-18:55",
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def fetch_timetable() -> list[dict]:
    session = get_session()
    resp = session.get(TIMETABLE_URL)
    resp.raise_for_status()
    return parse_timetable(resp.text)


def parse_timetable(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    timetable = []

    table = soup.find("table", {"id": "timetable"})
    if not table:
        tables = soup.find_all("table")
        for t in tables:
            if t.find("th") and "Mon" in t.get_text():
                table = t
                break

    if not table:
        return timetable

    rows = table.find_all("tr")
    headers = [th.get_text().strip() for th in rows[0].find_all("th")] if rows else []

    for row in rows[1:]:
        cols = row.find_all("td")
        if not cols:
            continue

        slot = cols[0].get_text().strip() if cols else ""
        timing = SLOT_TIMINGS.get(slot, slot)

        for i, col in enumerate(cols[1:], 1):
            text = col.get_text().strip()
            if text and i <= len(DAYS):
                timetable.append({
                    "day": DAYS[i - 1] if i <= len(DAYS) else f"Day {i}",
                    "slot": slot,
                    "time": timing,
                    "subject": text,
                    "room": extract_room(col),
                })

    return timetable


def extract_room(cell) -> str:
    small = cell.find("small")
    if small:
        return small.get_text().strip()
    text = cell.get_text().strip()
    parts = text.split("\n")
    return parts[-1].strip() if len(parts) > 1 else ""


def get_today_schedule(timetable: list[dict]) -> list[dict]:
    today = DAYS[datetime.now().weekday()] if datetime.now().weekday() < 6 else None
    if not today:
        return []
    return sorted(
        [e for e in timetable if e["day"] == today],
        key=lambda x: x["time"]
    )


def get_day_schedule(timetable: list[dict], day: str) -> list[dict]:
    day_lower = day.lower()
    matches = [e for e in timetable if e["day"].lower().startswith(day_lower)]
    return sorted(matches, key=lambda x: x["time"])


def find_prof_classes(timetable: list[dict], prof_name: str) -> list[dict]:
    return [e for e in timetable if prof_name.lower() in e["subject"].lower()]


def generate_ics(timetable: list[dict], semester_start: str = "") -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//iitkgp-erp-mcp//EN",
        "CALSCALE:GREGORIAN",
    ]

    if not semester_start:
        today = datetime.now()
        # Find next Monday
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        semester_start_date = today + timedelta(days=days_ahead)
    else:
        semester_start_date = datetime.strptime(semester_start, "%Y-%m-%d")

    for entry in timetable:
        if not entry["time"] or "-" not in entry["time"]:
            continue

        day_idx = DAYS.index(entry["day"]) if entry["day"] in DAYS else -1
        if day_idx < 0:
            continue

        event_date = semester_start_date + timedelta(days=day_idx)
        start_time, end_time = entry["time"].split("-")

        dtstart = event_date.strftime("%Y%m%d") + "T" + start_time.replace(":", "") + "00"
        dtend = event_date.strftime("%Y%m%d") + "T" + end_time.replace(":", "") + "00"

        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{entry['subject']}",
            f"LOCATION:{entry.get('room', '')}",
            f"RRULE:FREQ=WEEKLY;COUNT=16",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)
