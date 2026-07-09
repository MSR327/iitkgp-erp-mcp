from bs4 import BeautifulSoup
from ..auth.login import get_session

GRADES_URL = "https://erp.iitkgp.ac.in/Academic/student_performance_cumulative.htm"
GRADE_POINTS = {
    "EX": 10, "A": 9, "B": 8, "C": 7, "D": 6, "P": 5, "F": 0,
}


def fetch_grades(semester: str | None = None) -> list[dict]:
    session = get_session()
    resp = session.get(GRADES_URL)
    resp.raise_for_status()
    return parse_grades(resp.text, semester)


def parse_grades(html: str, semester: str | None = None) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    grades = []

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        current_sem = None

        for row in rows:
            header = row.find("th")
            if header and "Semester" in header.get_text():
                current_sem = header.get_text().strip()

            cols = row.find_all("td")
            if len(cols) >= 5:
                subject = {
                    "semester": current_sem,
                    "code": cols[0].get_text().strip(),
                    "name": cols[1].get_text().strip(),
                    "credits": int(cols[2].get_text().strip() or 0),
                    "grade": cols[3].get_text().strip(),
                    "grade_point": GRADE_POINTS.get(cols[3].get_text().strip(), 0),
                }
                if semester is None or current_sem == semester:
                    grades.append(subject)

    return grades


def calculate_cgpa(grades: list[dict]) -> float:
    total_credits = 0
    total_points = 0

    for g in grades:
        if g["grade"] in ("F", "I", "P", ""):
            continue
        total_credits += g["credits"]
        total_points += g["credits"] * g["grade_point"]

    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)


def calculate_sgpa(grades: list[dict], semester: str) -> float:
    sem_grades = [g for g in grades if g["semester"] == semester]
    return calculate_cgpa(sem_grades)


def get_cgpa_trend(grades: list[dict]) -> list[dict]:
    semesters = sorted(set(g["semester"] for g in grades if g["semester"]))
    trend = []
    for sem in semesters:
        sgpa = calculate_sgpa(grades, sem)
        all_up_to = [g for g in grades if g["semester"] and g["semester"] <= sem]
        cgpa = calculate_cgpa(all_up_to)
        trend.append({"semester": sem, "sgpa": sgpa, "cgpa": cgpa})
    return trend


def compare_subjects(grades: list[dict], subjects: list[str]) -> list[dict]:
    results = []
    for g in grades:
        if g["code"] in subjects or g["name"].lower() in [s.lower() for s in subjects]:
            results.append(g)
    return results


def what_if_cgpa(grades: list[dict], projected: list[dict]) -> float:
    all_grades = grades + [
        {**p, "grade_point": GRADE_POINTS.get(p["grade"], 0)}
        for p in projected
    ]
    return calculate_cgpa(all_grades)


def grade_distribution(grades: list[dict]) -> dict:
    dist = {}
    for g in grades:
        grade = g["grade"]
        if grade:
            dist[grade] = dist.get(grade, 0) + 1
    return dist
