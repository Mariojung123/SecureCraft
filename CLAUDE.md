# Project: SecureCraft — Secure Coding Education Platform

## Overview
A hands-on security education platform where users:
1. Select a challenge and choose a language (Python / PHP / Java)
2. Write defensive code in a skeleton template (Monaco editor)
3. Submit code → backend simultaneously:
   - Runs attack.sh inside a Docker sandbox to validate the code
   - Spins up a live sandbox container (iframe) for manual testing
4. User manually tests by injecting attack payloads into the live sandbox
5. After practice, user views a Report page with:
   - Vulnerable lines highlighted (dynamic vuln_patterns detection)
   - AI-generated severity badge, explanation, fix hint
   - AI chat interface for follow-up questions

## Tech Stack
- Backend: Flask (Python), MariaDB, Docker SDK, Anthropic SDK
- Frontend: React + Vite (JavaScript only, NO TypeScript), Monaco Editor, Tailwind CSS
- Sandbox: Docker containers (isolated per challenge, strict security constraints)
- AI: Claude API (model: claude-sonnet-4-20250514)

## Project Structure
- backend/app.py → Flask entry point + all API routes + find_vuln_lines()
- backend/ai_analyzer.py → analyze_code_with_ai(), chat_with_ai()
- backend/sandbox/orchestrator.py → Docker SDK container lifecycle management
- backend/.env → ANTHROPIC_API_KEY, PROBLEMS_DIR=../problems
- problems/<challenge_name>/ → meta.json, skeleton_python.py, solution_python.py, attack.sh, check.py
- frontend/src/pages/ → ChallengeList, ChallengeDetail, Sandbox, Report
- frontend/src/components/ → Navbar, ChallengeCard, CodeEditor (Monaco), Badge

## API Endpoints
- GET  /api/challenges → list all challenges
- GET  /api/challenges/<id>?language=python → get challenge detail + skeleton code
- POST /api/submit → receive user code + language, run attack.sh + create sandbox container
- GET  /api/sessions/<session_id> → poll validation result + AI analysis result
- POST /api/chat → AI chat with problem context { session_id, message, history }
- GET  /api/report/<session_id> → return full validation report

## Sandbox Security Constraints (non-negotiable)
- network_mode: none
- mem_limit: 128m
- cpu_quota: 50000
- read_only: true
- security_opt: no-new-privileges
- cap_drop: ALL
- user: non-root (1000:1000)
- auto-remove after TTL=60s

## meta.json Structure (per problem)
{
  "id": "problem_id",
  "title": "Problem Title",
  "language": "python",
  "languages": ["python", "php", "java"],
  "vuln_patterns": {
    "python": ["regex_pattern_1", "regex_pattern_2"],
    "php":    ["regex_pattern_1"],
    "java":   ["regex_pattern_1"]
  }
}

## Challenge File Structure (per problem)
- meta.json → id, title, language, languages, vuln_patterns (per-language regex dict)
- skeleton_python.py → vulnerable Python implementation for student to fix
- solution_python.py → correct secure Python implementation
- skeleton_php.php → (coming soon)
- skeleton_java.java → (coming soon)
- attack.sh → uses Python urllib only (NO curl, NO wget)
- check.py → prints exactly VULNERABLE or SECURE as result

## Code Style Rules
- Python: snake_case, small single-responsibility functions
- React: functional components + hooks only, no class components
- JavaScript only (NO TypeScript)
- All variable names, comments, and commit messages in English
- load_dotenv(override=True) must be called before os.environ.get()

## Current Challenges (10 total)
command_injection, sql_injection_login, sql_injection_search,
xss_reflected, xss_stored, path_traversal, hardcoded_credentials,
idor_user_data, missing_rate_limiting, weak_password_hashing

## Completed Features
- All 10 skeleton_python.py with vulnerable implementations
- Dynamic vuln_lines via regex vuln_patterns in meta.json (per-language dict)
- find_vuln_lines() in app.py for dynamic line detection (regex fallback)
- Multi-language tab UI: Python/PHP/Java (PHP & Java show Coming Soon)
- Claude AI analysis: vuln_lines, severity (HIGH/MEDIUM/LOW), explanation, fix_hint
- Claude AI chat: POST /api/chat with problem context system prompt
- Report page: SeverityBadge, AI explanation, AI chat UI with bubble styling

## Next Tasks
1. PHP skeleton_php.php for all 10 problems
2. Java skeleton_java.java for all 10 problems
3. Docker security hardening: network=none, cap_drop=ALL, read_only=true, container count limit
4. Report page: "Why defense failed" + "Improvement suggestions" AI sections
5. E2E test remaining 9 problems (command_injection already verified)