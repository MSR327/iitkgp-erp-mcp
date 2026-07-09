from bs4 import BeautifulSoup
from ..auth.login import get_session

ATTENDANCE_URL = "https://erp.iitkgp.ac.in/Academic/attendence_report.htm"


def fetch_attendance() -> list[dict]:
    session = get_session()
    resp = session.get(ATTENDANCE_URL)
    resp.raise_for_status()
    return parse_attendance(resp.text)


def parse_attendance(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    records = []

    table = soup.find("table", {"id": "attendence_report"})
    if not table:
        tables = soup.find_all("table")
        table = tables[0] if tables else None

    if not table:
        return records

    rows = table.find_all("tr")[1:]  # skip header
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            total = int(cols[3].get_text().strip() or 0)
            present = int(cols[4].get_text().strip() or 0)
            percentage = round((present / total) * 100, 1) if total > 0 else 0.0

            records.append({
                "code": cols[0].get_text().strip(),
                "name": cols[1].get_text().strip(),
                "type": cols[2].get_text().strip(),
                "total_classes": total,
                "present": present,
                "percentage": percentage,
            })

    return records


def attendance_alerts(records: list[dict], threshold: float = 80.0) -> list[dict]:
    return [r for r in records if r["percentage"] < threshold]


def classes_to_attend(record: dict, threshold: float = 80.0) -> int:
    if record["percentage"] >= threshold:
        return 0
    needed = record["total_classes"] * threshold / 100
    deficit = needed - record["present"]
    # Each class you attend increases both total and present by 1
    # Need: (present + x) / (total + x) >= threshold/100
    # Solving: x = ceil((threshold*total - 100*present) / (100 - threshold))
    t = threshold / 100
    x = (t * record["total_classes"] - record["present"]) / (1 - t)
    return max(0, int(x) + 1)


def classes_can_skip(record: dict, threshold: float = 80.0) -> int:
    if record["percentage"] <= threshold:
        return 0
    # Can skip x classes while staying above threshold
    # (present) / (total + x) >= threshold/100
    # x <= (100*present - threshold*total) / threshold
    t = threshold / 100
    x = (record["present"] - t * record["total_classes"]) / t
    return max(0, int(x))
