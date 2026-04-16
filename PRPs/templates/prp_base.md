name: "SecureCraft PRP Template — Context-Rich with Validation Loops"
description: |
  SecureCraft 프로젝트 전용 PRP 템플릿.
  Flask + React + Docker + Claude AI 스택 기반.

## Core Principles
1. **Context is King**: 필요한 모든 문서, 예제, 주의사항 포함
2. **Validation Loops**: AI가 직접 실행하고 수정할 수 있는 검증 명령 제공
3. **Follow CLAUDE.md**: 모든 코드 스타일 규칙 준수
4. **Progressive Success**: 단순한 것부터 검증 후 확장

---

## Goal
[구현할 기능 — 최종 상태를 구체적으로 기술]

## Why
- [사용자/학습자에게 주는 가치]
- [기존 기능과의 연관성]
- [해결하는 문제]

## What
[사용자에게 보이는 동작 + 기술적 요구사항]

### Success Criteria
- [ ] [측정 가능한 구체적 완료 조건]

---

## All Needed Context

### Documentation & References
\`\`\`yaml
- file: CLAUDE.md
  why: 프로젝트 전체 규칙 — 코드 스타일, API 엔드포인트, 보안 제약

- file: examples/flask_api_route_example.py
  why: Flask 라우트, 세션 관리, 백그라운드 스레드 패턴

- file: examples/ai_analyzer_example.py
  why: Claude API 호출, JSON 파싱, markdown fence 제거 패턴

- file: examples/react_page_example.jsx
  why: React 페이지 구조, polling, Tailwind 다크 테마 패턴

- file: examples/problem_meta_example.json
  why: meta.json 구조 — vuln_patterns 언어별 dict 형식
\`\`\`

### Known Gotchas
\`\`\`python
# CRITICAL: load_dotenv(override=True) must be called BEFORE os.environ.get()
# CRITICAL: vuln_patterns in meta.json is a language-keyed dict, not a flat list
# CRITICAL: Docker sandbox constraints are non-negotiable security requirements
# CRITICAL: React is JavaScript only — never use TypeScript (.tsx, .ts)
# PATTERN: AI call failures must always fall back to regex (never crash the request)
\`\`\`

---

## Implementation Blueprint

### Tasks (in order)
\`\`\`yaml
Task 1:
  [파일명]: [수정/생성 내용]
Task 2:
  ...
\`\`\`

---

## Validation Loop

### Level 1: Python Syntax Check
\`\`\`bash
cd backend
python -m py_compile app.py && echo "OK: app.py"
python -m py_compile ai_analyzer.py && echo "OK: ai_analyzer.py"
\`\`\`

### Level 2: Backend Smoke Test
\`\`\`bash
cd backend && python app.py &
sleep 2
curl -s http://localhost:5001/api/challenges | python -m json.tool | head -20
kill %1
\`\`\`

### Level 3: Frontend Build Check
\`\`\`bash
cd frontend && npm run build 2>&1 | tail -10
\`\`\`

---

## Final Validation Checklist
- [ ] python -m py_compile 에러 없음
- [ ] npm run build 에러 없음
- [ ] API 엔드포인트 응답 정상
- [ ] CLAUDE.md 코드 스타일 준수
- [ ] Docker 보안 제약 변경 없음
- [ ] AI 실패 시 fallback 동작 확인
- [ ] 기존 10개 챌린지 동작 회귀 없음

## Anti-Patterns to Avoid
- No TypeScript (.ts, .tsx)
- No class components in React
- No Docker security constraint relaxation
- No missing AI fallback (must not 500 on AI failure)
- No load_dotenv() omission
- No flat vuln_patterns (must be language-keyed dict)
