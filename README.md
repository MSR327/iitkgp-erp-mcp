# iitkgp-erp-mcp

MCP server for IIT Kharagpur ERP. Query your grades, CGPA, attendance, and more through Claude.

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

## Usage with Claude

Add to your `.mcp.json` or Claude Desktop config:

```json
{
  "mcpServers": {
    "iitkgp-erp": {
      "command": "iitkgp-erp-mcp"
    }
  }
}
```

Then ask Claude:
- "What's my CGPA?"
- "Show my grades for semester 4"
- "Compare my performance in CS vs MA subjects"
- "If I get A in all subjects this sem, what's my CGPA?"
- "Which subjects am I weakest in?"

## Available Tools

| Tool | Description |
|------|-------------|
| `erp_login` | Login to ERP (handles OTP) |
| `get_grades` | Fetch grades (all or specific semester) |
| `get_cgpa` | Current CGPA |
| `get_sgpa` | SGPA for a semester |
| `get_cgpa_trend` | Semester-wise progression |
| `compare_subjects` | Compare across subjects |
| `what_if_cgpa` | Projected CGPA calculator |
| `get_grade_distribution` | Grade breakdown (A/B/C/D counts) |

## Security

- Credentials stored in OS keychain (never plaintext)
- Session is local to your machine
- OTP entered live, never stored
- Nothing sensitive is committed to git

## Roadmap

- [ ] Attendance tracking + alerts
- [ ] Timetable extraction
- [ ] Elective recommender
- [ ] Placement notice integration
- [ ] Calendar sync

## License

MIT
