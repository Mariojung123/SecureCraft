# ── Claude AI Analyzer Pattern ────────────────────────────────────────────────
# Reference: backend/ai_analyzer.py
# Pattern: Lazy singleton client, structured JSON prompt, markdown fence stripping

import json
import os
import anthropic

_client = None

def _get_client() -> anthropic.Anthropic:
    """Lazy singleton — only initialized on first call."""
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def call_claude_for_json(prompt: str, max_tokens: int = 1000) -> dict:
    """
    Standard pattern for calling Claude and parsing JSON response.
    - Always strip markdown fences (Claude sometimes wraps JSON in ```json)
    - Raises json.JSONDecodeError on parse failure — let caller handle fallback
    """
    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def call_claude_for_text(system_prompt: str, history: list, user_message: str) -> str:
    """
    Standard pattern for conversational Claude call with history.
    history = [{"role": "user"|"assistant", "content": str}, ...]
    """
    messages = [*history, {"role": "user", "content": user_message}]
    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=messages,
    )
    return message.content[0].text


# ── JSON prompt template for structured output ─────────────────────────────────
# CRITICAL: Always instruct "Return ONLY a valid JSON object with NO extra text"
ANALYSIS_PROMPT_TEMPLATE = """You are a security expert analyzing student code.
Problem: {problem_title} ({problem_id})
Language: {language}

Return ONLY a valid JSON object with NO extra text, markdown, or explanation outside the JSON:
{{
  "vuln_lines": [1-based line numbers],
  "severity": "HIGH" or "MEDIUM" or "LOW" or "NONE",
  "explanation": "1-2 sentences",
  "fix_hint": "1-2 sentences",
  "is_vulnerable": true or false
}}

Code:
{numbered_code}"""
