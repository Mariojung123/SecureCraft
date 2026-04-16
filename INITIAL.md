## FEATURE
[Describe the feature you want to implement in specific detail]

Examples:
- "Generate skeleton_php.php for all 10 problems, reflecting PHP-specific vulnerability patterns and adding php key to vuln_patterns in each meta.json"
- "Add 'Why defense failed' and 'Improvement suggestions' AI sections to the Report page"
- "Docker security hardening: enforce network=none, cap_drop=ALL, read_only=true, and add concurrent container limit"

## EXAMPLES
[List of example files to reference]

examples/flask_api_route_example.py     # Flask route, session management, background thread patterns
examples/ai_analyzer_example.py         # Claude API call pattern (JSON parsing + markdown fence stripping)
examples/react_page_example.jsx         # React page structure, polling, Tailwind dark theme pattern
examples/problem_meta_example.json      # meta.json structure (language-keyed vuln_patterns format)

## DOCUMENTATION
[Relevant files and references]

CLAUDE.md                               # Project-wide rules (must read first)
backend/app.py                          # Existing Flask route patterns
backend/ai_analyzer.py                  # Existing AI analysis patterns
frontend/src/pages/Report.jsx           # Existing page pattern
problems/command_injection/             # Reference for existing problem file structure

## OTHER CONSIDERATIONS
[Constraints and common pitfalls]

- load_dotenv(override=True) must be called at the top of the file, before any os.environ.get()
- React: functional components + hooks only — no class components
- JavaScript only — TypeScript (.ts, .tsx) is strictly forbidden
- All variable names, comments, and commit messages must be in English
- Docker sandbox: network_mode=none and mem_limit=128m are non-negotiable security constraints — never relax them
- AI calls must always have a regex fallback on failure (see ai_analyzer.py pattern)
- vuln_patterns in meta.json must remain a language-keyed dict, never a flat list
