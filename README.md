# iitkgp-erp-mcp

MCP server for IIT Kharagpur ERP. Query your grades, CGPA, attendance, timetable, placements, and more through any AI agent.

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
- "What's my schedule today?"
- "Export my timetable to Google Calendar"
- "Browse the fee payment page"

## Available Tools (25)

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

### Timetable & Schedule
| Tool | Description |
|------|-------------|
| `get_timetable` | Full week or specific day schedule |
| `get_today_classes` | Today's classes |
| `where_is_prof` | Find a professor's location via timetable |
| `export_timetable_ics` | Export to ICS format (Google Calendar, Apple Calendar) |

### Placements & Notices
| Tool | Description |
|------|-------------|
| `get_placement_notices` | CDC notices, filterable by keyword |
| `get_notice_detail` | Full text of a specific notice |
| `get_academic_notices` | Academic announcements |

### Explorer
| Tool | Description |
|------|-------------|
| `browse_erp_page` | Navigate any ERP page freely |
| `search_erp_pages` | Find ERP pages by keyword |

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

## Grading Scale

| Grade | Points |
|-------|--------|
| EX | 10 |
| A | 9 |
| B | 8 |
| C | 7 |
| D | 6 |
| P | 5 |
| F | 0 |

## Roadmap

- [x] Grades & GPA tools
- [x] Attendance tracking + alerts
- [x] Elective recommender
- [x] Placement notice integration
- [x] Timetable extraction
- [x] Calendar sync (ICS export)
- [x] Prof finder
- [x] Academic notices
- [x] Freeform ERP browser
- [ ] Batch grade distributions (historical data)
- [ ] Registration status
- [ ] Fee payment status
- [ ] Hostel info

## Contributing

PRs welcome! The scrapers in `src/scrapers/` may need selector updates if ERP changes its HTML structure.

## License

MIT
