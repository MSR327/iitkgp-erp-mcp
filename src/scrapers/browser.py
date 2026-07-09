from bs4 import BeautifulSoup
from ..auth.login import get_session

ERP_BASE = "https://erp.iitkgp.ac.in"


def browse_page(path: str) -> dict:
    session = get_session()
    url = path if path.startswith("http") else f"{ERP_BASE}/{path.lstrip('/')}"
    resp = session.get(url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "link", "meta"]):
        tag.decompose()

    title = soup.find("title")
    title_text = title.get_text().strip() if title else ""

    tables = []
    for table in soup.find_all("table"):
        rows = []
        for row in table.find_all("tr"):
            cells = [cell.get_text().strip() for cell in row.find_all(["td", "th"])]
            if any(cells):
                rows.append(cells)
        if rows:
            tables.append(rows)

    links = []
    for a in soup.find_all("a", href=True):
        text = a.get_text().strip()
        href = a["href"]
        if text and not href.startswith("#") and not href.startswith("javascript"):
            links.append({"text": text, "href": href})

    body_text = soup.get_text(separator="\n", strip=True)
    body_text = "\n".join(line for line in body_text.split("\n") if line.strip())

    return {
        "url": url,
        "title": title_text,
        "tables": tables[:5],
        "links": links[:20],
        "text": body_text[:3000],
    }


def search_erp(query: str) -> list[dict]:
    common_pages = {
        "grades": "Academic/student_performance_cumulative.htm",
        "attendance": "Academic/attendence_report.htm",
        "timetable": "Academic/timetable_student.htm",
        "registration": "Academic/registration.htm",
        "fee": "Fees/student_fees.htm",
        "notices": "Academic/notices.htm",
        "placements": "TrainingPlacementSSO/NoticeList.jsp",
        "profile": "StudentProfile/student_profile.htm",
        "hostel": "Hostel/hostel_student.htm",
        "library": "Library/library_student.htm",
        "scholarship": "Scholarship/scholarship_student.htm",
    }

    results = []
    query_lower = query.lower()
    for key, path in common_pages.items():
        if query_lower in key:
            results.append({"page": key, "path": path, "url": f"{ERP_BASE}/{path}"})

    return results
