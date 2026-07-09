from bs4 import BeautifulSoup
from ..auth.login import get_session
from .grades import fetch_grades, GRADE_POINTS

SUBJECT_LIST_URL = "https://erp.iitkgp.ac.in/Academic/subject_list.htm"
GRADE_HISTORY_URL = "https://erp.iitkgp.ac.in/Academic/grading_history.htm"


def fetch_available_electives(elective_type: str = "breadth") -> list[dict]:
    session = get_session()
    resp = session.get(SUBJECT_LIST_URL)
    resp.raise_for_status()
    return parse_subject_list(resp.text, elective_type)


def parse_subject_list(html: str, elective_type: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    subjects = []

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 4:
                subject = {
                    "code": cols[0].get_text().strip(),
                    "name": cols[1].get_text().strip(),
                    "credits": int(cols[2].get_text().strip() or 0),
                    "department": cols[3].get_text().strip() if len(cols) > 3 else "",
                    "type": cols[4].get_text().strip() if len(cols) > 4 else "",
                }
                if elective_type.lower() in subject.get("type", "").lower():
                    subjects.append(subject)

    return subjects


def analyze_strengths(grades: list[dict]) -> dict:
    dept_scores = {}
    for g in grades:
        dept = g["code"][:2] if g["code"] else "XX"
        if dept not in dept_scores:
            dept_scores[dept] = {"total_points": 0, "total_credits": 0, "subjects": []}

        gp = GRADE_POINTS.get(g["grade"], 0)
        if g["grade"] not in ("F", ""):
            dept_scores[dept]["total_points"] += gp * g["credits"]
            dept_scores[dept]["total_credits"] += g["credits"]
            dept_scores[dept]["subjects"].append(g)

    for dept, data in dept_scores.items():
        if data["total_credits"] > 0:
            data["avg_gpa"] = round(data["total_points"] / data["total_credits"], 2)
        else:
            data["avg_gpa"] = 0

    return dept_scores


def recommend_electives(grades: list[dict], available: list[dict] = None) -> list[dict]:
    strengths = analyze_strengths(grades)

    strong_depts = sorted(
        strengths.items(),
        key=lambda x: x[1]["avg_gpa"],
        reverse=True
    )

    recommendations = []
    for dept_code, data in strong_depts[:5]:
        recommendations.append({
            "department_code": dept_code,
            "your_avg_gpa": data["avg_gpa"],
            "subjects_taken": len(data["subjects"]),
            "reasoning": f"You average {data['avg_gpa']}/10 in {dept_code} subjects",
        })

    if available:
        scored_electives = []
        for elective in available:
            dept = elective["code"][:2]
            dept_data = strengths.get(dept, {"avg_gpa": 5})
            scored_electives.append({
                **elective,
                "predicted_comfort": dept_data["avg_gpa"],
                "reasoning": f"Based on your {dept_data['avg_gpa']}/10 avg in {dept} subjects"
            })
        scored_electives.sort(key=lambda x: x["predicted_comfort"], reverse=True)
        return scored_electives[:10]

    return recommendations


def find_strong_weak_subjects(grades: list[dict]) -> dict:
    if not grades:
        return {"strong": [], "weak": []}

    sorted_grades = sorted(
        [g for g in grades if g["grade"] and g["grade"] != "F"],
        key=lambda x: GRADE_POINTS.get(x["grade"], 0),
        reverse=True
    )

    return {
        "strong": sorted_grades[:5],
        "weak": sorted_grades[-5:] if len(sorted_grades) >= 5 else sorted_grades,
    }
