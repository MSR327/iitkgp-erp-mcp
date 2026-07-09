from bs4 import BeautifulSoup
from ..auth.login import get_session

REGISTRATION_URL = "https://erp.iitkgp.ac.in/Academic/registration.htm"
REGISTERED_SUBJECTS_URL = "https://erp.iitkgp.ac.in/Academic/student_registered_subjects.htm"


def fetch_registered_subjects() -> list[dict]:
    session = get_session()
    resp = session.get(REGISTERED_SUBJECTS_URL)
    resp.raise_for_status()
    return parse_registered_subjects(resp.text)


def parse_registered_subjects(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    subjects = []

    table = soup.find("table")
    if not table:
        return subjects

    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            subjects.append({
                "code": cols[0].get_text().strip(),
                "name": cols[1].get_text().strip(),
                "credits": int(cols[2].get_text().strip() or 0),
                "type": cols[3].get_text().strip() if len(cols) > 3 else "",
                "slot": cols[4].get_text().strip() if len(cols) > 4 else "",
                "prof": cols[5].get_text().strip() if len(cols) > 5 else "",
            })

    return subjects


def get_credit_summary(subjects: list[dict]) -> dict:
    summary = {"total": 0, "by_type": {}}
    for s in subjects:
        summary["total"] += s["credits"]
        stype = s["type"] or "Unknown"
        if stype not in summary["by_type"]:
            summary["by_type"][stype] = {"credits": 0, "count": 0, "subjects": []}
        summary["by_type"][stype]["credits"] += s["credits"]
        summary["by_type"][stype]["count"] += 1
        summary["by_type"][stype]["subjects"].append(s["code"])

    return summary


def check_slot_conflicts(subjects: list[dict]) -> list[dict]:
    slot_map = {}
    conflicts = []

    for s in subjects:
        if not s["slot"]:
            continue
        for slot in s["slot"].split(","):
            slot = slot.strip()
            if slot in slot_map:
                conflicts.append({
                    "slot": slot,
                    "subject_1": slot_map[slot],
                    "subject_2": f"{s['code']} ({s['name']})",
                })
            else:
                slot_map[slot] = f"{s['code']} ({s['name']})"

    return conflicts
