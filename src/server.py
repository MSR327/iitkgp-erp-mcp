import json
from mcp.server.fastmcp import FastMCP
from .auth.login import login, is_logged_in, logout
from .scrapers.grades import (
    fetch_grades,
    calculate_cgpa,
    calculate_sgpa,
    get_cgpa_trend,
    compare_subjects,
    what_if_cgpa,
    grade_distribution,
)
from .scrapers.attendance import (
    fetch_attendance,
    attendance_alerts,
    classes_to_attend,
    classes_can_skip,
)
from .scrapers.electives import (
    fetch_available_electives,
    recommend_electives,
    find_strong_weak_subjects,
    analyze_strengths,
)
from .scrapers.placements import (
    fetch_placement_notices,
    fetch_notice_detail,
    filter_notices,
)
from .scrapers.timetable import (
    fetch_timetable,
    get_today_schedule,
    get_day_schedule,
    find_prof_classes,
    generate_ics,
)
from .scrapers.browser import browse_page, search_erp
from .scrapers.notices import fetch_academic_notices, search_notices
from .scrapers.registration import (
    fetch_registered_subjects,
    get_credit_summary,
    check_slot_conflicts,
)
from .utils import cache

mcp = FastMCP("iitkgp-erp", "MCP server for IIT Kharagpur ERP")


@mcp.tool()
def erp_login(otp: str = "") -> str:
    """Login to IIT KGP ERP. If OTP is required, pass it as a parameter."""
    try:
        login(otp_input=otp if otp else None)
        return "Successfully logged in to ERP."
    except Exception as e:
        return f"Login failed: {e}"


@mcp.tool()
def erp_logout() -> str:
    """Logout from ERP and clear the session."""
    logout()
    return "Logged out."


@mcp.tool()
def get_grades(semester: str = "") -> str:
    """Fetch grades. Pass semester like 'Semester 3' to filter, or leave empty for all."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        grades = fetch_grades(semester if semester else None)
        if not grades:
            return "No grades found."
        return json.dumps(grades, indent=2)
    except Exception as e:
        return f"Error fetching grades: {e}"


@mcp.tool()
def get_cgpa() -> str:
    """Get your current CGPA."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        grades = fetch_grades()
        cgpa = calculate_cgpa(grades)
        return f"Your CGPA: {cgpa}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_sgpa(semester: str) -> str:
    """Get SGPA for a specific semester. Example: 'Semester 3'"""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        grades = fetch_grades()
        sgpa = calculate_sgpa(grades, semester)
        return f"SGPA for {semester}: {sgpa}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_cgpa_trend_tool() -> str:
    """Get semester-wise CGPA and SGPA progression."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        grades = fetch_grades()
        trend = get_cgpa_trend(grades)
        return json.dumps(trend, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def compare_subjects_tool(subjects: str) -> str:
    """Compare performance across subjects. Pass comma-separated codes or names.
    Example: 'CS10001,MA10001' or 'Programming,Mathematics'"""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        subject_list = [s.strip() for s in subjects.split(",")]
        grades = fetch_grades()
        results = compare_subjects(grades, subject_list)
        if not results:
            return "No matching subjects found."
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def what_if_cgpa_tool(projected_grades: str) -> str:
    """Calculate projected CGPA with hypothetical grades.
    Pass as JSON: [{"credits": 4, "grade": "A"}, {"credits": 3, "grade": "B"}]"""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        projected = json.loads(projected_grades)
        grades = fetch_grades()
        new_cgpa = what_if_cgpa(grades, projected)
        current = calculate_cgpa(grades)
        return f"Current CGPA: {current}\nProjected CGPA: {new_cgpa}"
    except json.JSONDecodeError:
        return "Invalid JSON. Use format: [{\"credits\": 4, \"grade\": \"A\"}]"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_grade_distribution_tool() -> str:
    """Get your grade distribution (count of each grade)."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        grades = fetch_grades()
        dist = grade_distribution(grades)
        return json.dumps(dist, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_attendance() -> str:
    """Get attendance for all subjects in current semester."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        cached = cache.get("attendance")
        if cached:
            records = cached
        else:
            records = fetch_attendance()
            cache.set("attendance", records, ttl=600)
        if not records:
            return "No attendance data found."
        return json.dumps(records, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_attendance_alerts(threshold: float = 80.0) -> str:
    """Get subjects where attendance is below threshold (default 80%)."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        records = fetch_attendance()
        alerts = attendance_alerts(records, threshold)
        if not alerts:
            return f"All subjects above {threshold}% attendance. You're safe!"
        return json.dumps(alerts, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def can_i_skip(subject_code: str) -> str:
    """Check how many classes you can skip for a subject and still stay above 80%."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        records = fetch_attendance()
        match = [r for r in records if r["code"] == subject_code]
        if not match:
            match = [r for r in records if subject_code.lower() in r["name"].lower()]
        if not match:
            return f"Subject '{subject_code}' not found. Use exact code or partial name."

        record = match[0]
        skippable = classes_can_skip(record)
        need = classes_to_attend(record)

        if record["percentage"] >= 80:
            return (
                f"{record['name']} ({record['code']})\n"
                f"Attendance: {record['percentage']}% ({record['present']}/{record['total_classes']})\n"
                f"You can skip {skippable} more classes and stay above 80%."
            )
        else:
            return (
                f"{record['name']} ({record['code']})\n"
                f"Attendance: {record['percentage']}% ({record['present']}/{record['total_classes']})\n"
                f"WARNING: Below 80%! You need to attend {need} more classes to recover."
            )
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def recommend_electives_tool(elective_type: str = "breadth") -> str:
    """Recommend electives based on your grade history and strengths.
    Types: 'breadth', 'depth', 'open'"""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        grades = fetch_grades()
        try:
            available = fetch_available_electives(elective_type)
        except Exception:
            available = None

        recs = recommend_electives(grades, available)
        if not recs:
            return "Could not generate recommendations. Try after fetching grades."
        return json.dumps(recs, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_strengths_weaknesses() -> str:
    """Find your strongest and weakest subjects based on grades."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        grades = fetch_grades()
        result = find_strong_weak_subjects(grades)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_department_performance() -> str:
    """See your average performance grouped by department (CS, MA, EE, etc.)."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        grades = fetch_grades()
        strengths = analyze_strengths(grades)
        summary = {
            dept: {"avg_gpa": data["avg_gpa"], "subjects_taken": len(data["subjects"])}
            for dept, data in sorted(strengths.items(), key=lambda x: x[1]["avg_gpa"], reverse=True)
        }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_placement_notices(keyword: str = "") -> str:
    """Get placement/internship notices from CDC. Optionally filter by keyword.
    Example: 'SDE', 'Google', 'internship'"""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        cached = cache.get("placement_notices")
        if cached:
            notices = cached
        else:
            notices = fetch_placement_notices()
            cache.set("placement_notices", notices, ttl=300)

        if not notices:
            return "No placement notices found."

        if keyword:
            notices = filter_notices(notices, keyword)
            if not notices:
                return f"No notices matching '{keyword}'."

        return json.dumps(notices[:20], indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_notice_detail(notice_url: str) -> str:
    """Get full details of a specific placement notice. Pass the URL from get_placement_notices."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        detail = fetch_notice_detail(notice_url)
        if not detail:
            return "Could not fetch notice details."
        return detail
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_timetable(day: str = "") -> str:
    """Get your timetable. Pass a day like 'Monday' to filter, or leave empty for full week."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        cached = cache.get("timetable")
        if cached:
            tt = cached
        else:
            tt = fetch_timetable()
            cache.set("timetable", tt, ttl=3600)

        if not tt:
            return "No timetable data found."

        if day:
            tt = get_day_schedule(tt, day)
            if not tt:
                return f"No classes on {day}."

        return json.dumps(tt, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_today_classes() -> str:
    """Get today's class schedule."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        cached = cache.get("timetable")
        if cached:
            tt = cached
        else:
            tt = fetch_timetable()
            cache.set("timetable", tt, ttl=3600)

        today = get_today_schedule(tt)
        if not today:
            return "No classes today!"
        return json.dumps(today, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def where_is_prof(prof_name: str) -> str:
    """Find where a professor is based on timetable data.
    Pass partial name like 'sharma' or 'Prof Kumar'."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        cached = cache.get("timetable")
        if cached:
            tt = cached
        else:
            tt = fetch_timetable()
            cache.set("timetable", tt, ttl=3600)

        classes = find_prof_classes(tt, prof_name)
        if not classes:
            return f"No classes found for '{prof_name}' in your timetable."
        return json.dumps(classes, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def export_timetable_ics(semester_start: str = "") -> str:
    """Export timetable as ICS (calendar) format. Optionally pass semester start date (YYYY-MM-DD).
    You can import the output into Google Calendar, Apple Calendar, etc."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        tt = fetch_timetable()
        if not tt:
            return "No timetable data found."
        ics = generate_ics(tt, semester_start)
        return ics
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def browse_erp_page(path: str) -> str:
    """Browse any ERP page. Pass a path like 'Academic/notices.htm' or full URL.
    Returns page title, text content, tables, and links found."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        result = browse_page(path)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def search_erp_pages(query: str) -> str:
    """Search for ERP pages by keyword. Returns matching page paths.
    Examples: 'grades', 'fee', 'hostel', 'library'"""
    results = search_erp(query)
    if not results:
        return f"No pages matching '{query}'. Try: grades, attendance, timetable, fee, notices, placements, profile, hostel, library, scholarship"
    return json.dumps(results, indent=2)


@mcp.tool()
def get_academic_notices(keyword: str = "") -> str:
    """Get academic notices/announcements. Optionally filter by keyword."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        cached = cache.get("academic_notices")
        if cached:
            notices = cached
        else:
            notices = fetch_academic_notices()
            cache.set("academic_notices", notices, ttl=300)

        if not notices:
            return "No academic notices found."

        if keyword:
            notices = search_notices(notices, keyword)
            if not notices:
                return f"No notices matching '{keyword}'."

        return json.dumps(notices[:20], indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_registered_subjects() -> str:
    """Get all subjects you're currently registered for this semester."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        subjects = fetch_registered_subjects()
        if not subjects:
            return "No registered subjects found."
        return json.dumps(subjects, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_credit_summary_tool() -> str:
    """Get credit summary — total credits and breakdown by type (core, elective, lab, etc.)."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        subjects = fetch_registered_subjects()
        summary = get_credit_summary(subjects)
        return json.dumps(summary, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def check_slot_conflicts_tool() -> str:
    """Check if any of your registered subjects have slot conflicts."""
    if not is_logged_in():
        return "Not logged in. Use erp_login first."
    try:
        subjects = fetch_registered_subjects()
        conflicts = check_slot_conflicts(subjects)
        if not conflicts:
            return "No slot conflicts found. Your schedule is clean!"
        return json.dumps(conflicts, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def clear_cache() -> str:
    """Clear locally cached ERP data."""
    cache.clear()
    return "Cache cleared."


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
