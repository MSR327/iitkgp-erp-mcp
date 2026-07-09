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


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
