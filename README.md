# iitkgp-erp-mcp

MCP server for IIT Kharagpur ERP. Query your grades, CGPA, attendance, placements, and more through any AI agent or MCP-compatible client.

Works with: **Claude Code, Claude Desktop, Cursor, Cline, Continue, Zed, custom agents** — anything that speaks MCP.

## Install

```bash
pip install iitkgp-erp-mcp
playwright install chromium
```

## Setup

```bash
iitkgp-erp-setup
```

This stores your credentials securely in your OS keychain.

## Usage

Add to your MCP client config (`.mcp.json`, `mcp_servers.json`, etc.):

```json
{
  "mcpServers": {
    "iitkgp-erp": {
      "command": "iitkgp-erp-mcp"
    }
  }
}
```

Then ask your AI agent:
- "What's my CGPA?"
- "Show my grades for semester 4"
- "Compare my performance in CS vs MA subjects"
- "If I get A in all subjects this sem, what's my CGPA?"
- "Which breadth electives should I take?"
- "Any new placement notices for SDE roles?"
- "Can I skip tomorrow's Signals class?"

## Available Tools

### Grades & GPA
| Tool | Description |
|------|-------------|
| `erp_login` | Login to ERP (handles OTP) |
| `erp_logout` | End session |
| `get_grades` | Fetch grades (all or specific semester) |
| `get_cgpa` | Current CGPA |
| `get_sgpa` | SGPA for a semester |
| `get_cgpa_trend` | Semester-wise CGPA/SGPA progression |
| `compare_subjects` | Compare across subjects |
| `what_if_cgpa` | Projected CGPA calculator |
| `get_grade_distribution` | Grade breakdown (EX/A/B/C/D/P/F counts) |

### Attendance
| Tool | Description |
|------|-------------|
| `get_attendance` | All subjects with attendance % |
| `get_attendance_alerts` | Subjects below 80% danger zone |
| `can_i_skip` | How many classes you can safely miss |

### Elective Recommender
| Tool | Description |
|------|-------------|
| `recommend_electives` | Suggests electives based on your grade patterns |
| `get_strengths_weaknesses` | Your top 5 best/worst subjects |
| `get_department_performance` | Average GPA by department |

### Placements
| Tool | Description |
|------|-------------|
| `get_placement_notices` | CDC notices, filterable by keyword |
| `get_notice_detail` | Full text of a specific notice |

### Utility
| Tool | Description |
|------|-------------|
| `clear_cache` | Clear locally cached data |

## Security

- Credentials stored in OS keychain (never plaintext)
- Session is local to your machine
- OTP entered live, never stored
- Nothing sensitive is committed to git

## How it works

```
Your AI Agent ←→ MCP Protocol (stdio) ←→ iitkgp-erp-mcp server
                                              │
                                              ├── iitkgp-erp-login (auth)
                                              ├── requests + BeautifulSoup (scraping)
                                              └── Playwright (JS-heavy pages)
                                              │
                                              ▼
                                        erp.iitkgp.ac.in
```

## Roadmap

- [x] Grades & GPA tools
- [x] Attendance tracking + alerts
- [x] Elective recommender
- [x] Placement notice integration
- [ ] Timetable extraction
- [ ] Calendar sync (Google Calendar / ICS)
- [ ] Prof finder (Where Is My Prof?)
- [ ] Batch grade distributions

## License

MIT
