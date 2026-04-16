import json
import os

import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        print(f"[ai_analyzer] API key loaded: {api_key[:10]}... (len={len(api_key)})", flush=True)
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def analyze_code_with_ai(
    code: str,
    language: str,
    problem_id: str,
    problem_title: str,
    problem_type: str = "",
) -> dict:
    """
    Ask Claude to locate vulnerable lines and produce educational feedback.

    Returns a dict with keys:
        vuln_lines              list[int]  1-based line numbers
        severity                str        "HIGH" | "MEDIUM" | "LOW" | "NONE"
        vulnerability_explanation str
        fix_hint                str
        is_vulnerable           bool
    Raises on network/parse error — callers should catch and fall back to regex.
    """
    numbered_code = "\n".join(f"{i+1:3d} | {line}" for i, line in enumerate(code.splitlines()))

    prompt = f"""You are a security expert analyzing student code for a secure coding education platform.
You are analyzing code for this specific vulnerability type: {problem_type or problem_id}

Problem: {problem_title} ({problem_id})
Language: {language}

Analyze the following {language} code and find security vulnerabilities.

Return ONLY a valid JSON object with NO extra text, markdown, or explanation outside the JSON:
{{
  "vuln_lines": [line numbers where the vulnerability exists, based on the numbered lines shown above. Return ONLY the lines that are directly vulnerable, not surrounding context.],
  "severity": "HIGH" or "MEDIUM" or "LOW",
  "vulnerability_explanation": "1-2 sentences explaining what makes this code vulnerable",
  "fix_hint": "1-2 sentences explaining how to fix it",
  "is_vulnerable": true or false
}}

If the code is already secure (uses parameterized queries, proper escaping, etc.), return:
{{
  "vuln_lines": [],
  "severity": "NONE",
  "vulnerability_explanation": "This code is properly secured.",
  "fix_hint": "",
  "is_vulnerable": false
}}

Code to analyze:
{numbered_code}"""

    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
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


def chat_with_ai(system_prompt: str, history: list, user_message: str) -> str:
    """
    Send a conversational message to Claude with full history context.

    history  — list of {"role": "user"|"assistant", "content": str}
    Returns the assistant reply text.
    Raises on API/network error — callers should catch.
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
