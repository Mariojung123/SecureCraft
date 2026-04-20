# 🔐 SecureCraft

> **A hands-on secure coding education platform** — learn to defend against real-world web vulnerabilities by writing, testing, and fixing code in an isolated sandbox environment, guided by AI-powered analysis.

📄 **[View Full Project Specification →](https://mariojung123.github.io/SecureCraft/securecraft-spec-en.html)**

---

## ✨ What is SecureCraft?

SecureCraft bridges the gap between *knowing* security theory and *actually writing* secure code. Instead of reading about SQL injection, you write vulnerable code, attack it yourself, get real-time feedback from Claude AI, and learn exactly how to fix it.

**The learning loop:**

```
Select Challenge → Write Defensive Code → Submit
       ↓
Attack Script validates your code in Docker sandbox
       ↓
Live sandbox iframe → inject payloads yourself
       ↓
AI Report: vulnerable lines highlighted + severity badge + fix hint
       ↓
AI Chat: ask follow-up questions in context
```

---

## 🚀 Features

- **10 OWASP Top 10 challenges** — each with a vulnerable skeleton you progressively harden
- **Real Docker sandboxing** — every submission runs in an isolated container with strict security constraints (no network, read-only FS, non-root user, memory & CPU limits)
- **Live sandbox iframe** — manually inject attack payloads into your running code
- **Multi-language support** — Python (fully implemented), PHP and Java (in progress)
- **AI-powered code analysis** — Claude detects vulnerable lines via regex + semantic understanding
- **Severity badges** — HIGH / MEDIUM / LOW rated by Claude per submission
- **Contextual AI chat** — ask Claude follow-up questions with full problem context
- **Monaco editor** — VS Code-quality editing experience in the browser

---

## 🛡️ Challenges Included

| # | Challenge | Category | Difficulty |
|---|-----------|----------|------------|
| 1 | Command Injection | OS Security | Medium |
| 2 | SQL Injection (Login) | Database | Medium |
| 3 | SQL Injection (Search) | Database | Medium |
| 4 | XSS Reflected | Web | Medium |
| 5 | XSS Stored | Web | Hard |
| 6 | Path Traversal | File System | Medium |
| 7 | Hardcoded Credentials | Secret Management | Easy |
| 8 | IDOR (User Data) | Access Control | Medium |
| 9 | Missing Rate Limiting | API Security | Easy |
| 10 | Weak Password Hashing | Cryptography | Medium |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Frontend                        │
│   React + Vite │ Monaco Editor │ Tailwind CSS       │
│   ChallengeList → ChallengeDetail → Sandbox/Report  │
└─────────────────────┬───────────────────────────────┘
                      │ REST API
┌─────────────────────▼───────────────────────────────┐
│                  Flask Backend                      │
│  app.py (routes + vuln detection)                   │
│  ai_analyzer.py (Claude API integration)            │
│  sandbox/orchestrator.py (Docker SDK)               │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
    ┌──────▼──────┐      ┌────────▼────────┐
    │   MariaDB   │      │  Docker Sandbox  │
    │  (sessions, │      │  per submission  │
    │   results)  │      │  (isolated env)  │
    └─────────────┘      └─────────────────┘
                                  │
                         ┌────────▼────────┐
                         │  Claude AI API   │
                         │  (analysis +    │
                         │   chat)         │
                         └─────────────────┘
```

---

## 🔒 Sandbox Security Constraints

Every user submission runs in a Docker container with hardened constraints — **non-negotiable by design**:

| Constraint | Value |
|---|---|
| Network | `none` (fully air-gapped) |
| Memory limit | `128MB` |
| CPU quota | `50,000` (50% of 1 core) |
| Filesystem | `read-only` |
| Privilege escalation | `no-new-privileges` |
| Linux capabilities | `ALL dropped` |
| User | `1000:1000` (non-root) |
| Auto-remove | After `60s` TTL |

---

## 🧰 Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Core language |
| Flask | 3.1.0 | REST API framework |
| Anthropic SDK | ≥0.40.0 | Claude AI integration |
| Docker SDK | 7.1.0 | Container orchestration |
| PyMySQL | 1.1.1 | MariaDB connector |
| python-dotenv | 1.0.1 | Environment config |

### Frontend
| Technology | Purpose |
|---|---|
| React 18 | UI framework (functional components + hooks) |
| Vite | Build tool & dev server |
| Monaco Editor | VS Code-quality code editor |
| Tailwind CSS | Utility-first styling |
| JavaScript (ES2022) | No TypeScript — intentionally simple |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker | Sandbox container runtime |
| MariaDB 11 | Session & result persistence |
| Docker Compose | Local development orchestration |

### AI
| Model | Usage |
|---|---|
| `claude-sonnet-4-20250514` | Code vulnerability analysis + contextual chat |

---

## 🧪 Testing

Backend tests live in `backend/tests/` and run with pytest — no external services or API keys required.

```bash
cd backend
python -m pytest tests/ -v
```

**42 tests across 3 files:**

| File | Tests | What it covers |
|---|---|---|
| `test_submit_service.py` | 21 | `find_vuln_lines` pattern matching, `_resolve_vuln_lines` AI/regex fallback logic, `_get_regex_vuln_lines` dict vs list format, `read_skeleton` file I/O |
| `test_ai_analyzer.py` | 11 | `_parse_analysis_response` plain JSON / markdown-fenced / invalid input, `build_chat_system_prompt` with full report / None / missing fields |
| `test_routes.py` | 10 | `GET /api/challenges`, `POST /api/submit` validation + happy path, `GET /api/report` for unknown / processing / done sessions |

All tests use temporary directories and mock Docker/AI calls — safe to run anywhere.

---

## 📁 Project Structure

```
SecureCraft/
├── backend/
│   ├── app.py                  # Flask entry point, all API routes, find_vuln_lines()
│   ├── ai_analyzer.py          # analyze_code_with_ai(), chat_with_ai()
│   ├── sandbox/
│   │   └── orchestrator.py     # Docker SDK container lifecycle management
│   ├── tests/
│   │   ├── test_submit_service.py
│   │   ├── test_ai_analyzer.py
│   │   └── test_routes.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── ChallengeList.jsx
│       │   ├── ChallengeDetail.jsx
│       │   ├── Sandbox.jsx
│       │   └── Report.jsx
│       └── components/
│           ├── CodeEditor.jsx  # Monaco wrapper
│           ├── Badge.jsx       # Severity badge (HIGH/MEDIUM/LOW)
│           ├── ChallengeCard.jsx
│           └── Navbar.jsx
├── problems/
│   └── <challenge_name>/
│       ├── meta.json           # Challenge metadata + vuln_patterns (per-language regex)
│       ├── skeleton_python.py  # Vulnerable starter code for students
│       ├── solution_python.py  # Secure reference implementation
│       ├── attack.sh           # Automated attack validation script
│       ├── check.py            # Prints VULNERABLE or SECURE
│       └── templates/          # HTML/PHP templates for live sandbox
└── docker-compose.yml
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/challenges` | List all challenges |
| `GET` | `/api/challenges/<id>?language=python` | Challenge detail + skeleton code |
| `POST` | `/api/submit` | Submit code → run attack.sh + spin up sandbox |
| `GET` | `/api/sessions/<session_id>` | Poll validation result + AI analysis |
| `POST` | `/api/chat` | AI chat with problem context |
| `GET` | `/api/report/<session_id>` | Full validation report |

---

## ⚡ Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Anthropic API key

### 1. Clone & configure

```bash
git clone https://github.com/Mariojung123/SecureCraft.git
cd SecureCraft
cp .env.example backend/.env
# Edit backend/.env and set your ANTHROPIC_API_KEY
```

### 2. Start the database

```bash
docker compose up -d
```

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) and start hacking.

---

## 🎯 How a Challenge Works

1. **Select** a challenge from the list (e.g., SQL Injection)
2. **Read** the problem description and vulnerable skeleton code
3. **Write** your defensive fix in the Monaco editor
4. **Submit** — the backend simultaneously:
   - Runs `attack.sh` inside a Docker sandbox to check if your code is exploitable
   - Spins up a live sandbox container exposed via iframe
5. **Test manually** — try injecting attack payloads into the running sandbox yourself
6. **View the Report** — see which lines Claude flagged, the severity rating, explanation, and fix hint
7. **Chat with Claude** — ask follow-up questions with full context of the challenge and your code

---

## 🤖 AI Analysis Details

Claude analyzes each submission with:

- **Vulnerable line detection** — regex-based `vuln_patterns` from `meta.json` combined with Claude's semantic understanding
- **Severity rating** — `HIGH`, `MEDIUM`, or `LOW` based on exploitability and impact
- **Explanation** — plain-language description of why the code is vulnerable
- **Fix hint** — concrete guidance without giving away the full solution
- **Contextual chat** — full problem context injected into Claude's system prompt for accurate answers

---

## 🗺️ Roadmap

- [x] 10 Python skeleton challenges
- [x] Docker sandbox orchestration with full security hardening
- [x] Claude AI vulnerability analysis + severity badges
- [x] AI contextual chat interface
- [x] PHP skeleton challenges (all 10)
- [ ] Java skeleton challenges (all 10)
- [ ] User authentication + progress tracking
- [ ] Leaderboard
- [ ] "Why defense failed" AI section in reports
- [ ] CI/CD pipeline with automated challenge validation

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <strong>Built to make secure coding tangible, not theoretical.</strong><br/>
  If this project helped you think more like an attacker — ⭐ star it.
</div>
