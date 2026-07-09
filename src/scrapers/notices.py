from bs4 import BeautifulSoup
from ..auth.login import get_session

ACADEMIC_NOTICES_URL = "https://erp.iitkgp.ac.in/Academic/notices.htm"


def fetch_academic_notices() -> list[dict]:
    session = get_session()
    resp = session.get(ACADEMIC_NOTICES_URL)
    resp.raise_for_status()
    return parse_notices(resp.text)


def parse_notices(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    notices = []

    table = soup.find("table")
    if not table:
        return notices

    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            link = cols[1].find("a") if len(cols) > 1 else None
            notice = {
                "date": cols[0].get_text().strip(),
                "title": cols[1].get_text().strip() if len(cols) > 1 else "",
                "link": link["href"] if link else "",
                "category": cols[2].get_text().strip() if len(cols) > 2 else "",
            }
            notices.append(notice)

    return notices


def search_notices(notices: list[dict], keyword: str) -> list[dict]:
    keyword_lower = keyword.lower()
    return [
        n for n in notices
        if keyword_lower in n["title"].lower()
        or keyword_lower in n.get("category", "").lower()
    ]
