from bs4 import BeautifulSoup
from ..auth.login import get_session

CDC_URL = "https://erp.iitkgp.ac.in/TrainingPlacementSSO/TPStudent.jsp"
NOTICES_URL = "https://erp.iitkgp.ac.in/TrainingPlacementSSO/NoticeList.jsp"


def fetch_placement_notices() -> list[dict]:
    session = get_session()
    resp = session.get(NOTICES_URL)
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
        if len(cols) >= 3:
            link = cols[1].find("a")
            notice = {
                "date": cols[0].get_text().strip(),
                "title": cols[1].get_text().strip(),
                "link": link["href"] if link else "",
                "company": cols[2].get_text().strip() if len(cols) > 2 else "",
                "type": cols[3].get_text().strip() if len(cols) > 3 else "",
            }
            notices.append(notice)

    return notices


def fetch_notice_detail(notice_url: str) -> str:
    session = get_session()
    resp = session.get(notice_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    content = soup.find("div", {"class": "notice-content"})
    if not content:
        content = soup.find("body")

    return content.get_text().strip() if content else ""


def filter_notices(notices: list[dict], keyword: str) -> list[dict]:
    keyword_lower = keyword.lower()
    return [
        n for n in notices
        if keyword_lower in n["title"].lower()
        or keyword_lower in n.get("company", "").lower()
        or keyword_lower in n.get("type", "").lower()
    ]
