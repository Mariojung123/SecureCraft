import json
import os

import anthropic

MODEL = "claude-sonnet-4-6"

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def _build_analysis_prompt(
    code: str,
    language: str,
    problem_id: str,
    problem_title: str,
    problem_type: str,
) -> str:
    numbered_code = "\n".join(f"{i+1:3d} | {line}" for i, line in enumerate(code.splitlines()))
    return f"""You are a security expert analyzing student code for a secure coding education platform.
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


def _parse_analysis_response(raw: str) -> dict:
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def analyze_code_with_ai(
    code: str,
    language: str,
    problem_id: str,
    problem_title: str,
    problem_type: str = "",
    client: anthropic.Anthropic | None = None,
) -> dict:
    """
    Returns dict with: vuln_lines, severity, vulnerability_explanation, fix_hint, is_vulnerable.
    Raises on network/parse error — callers should catch and fall back to regex.
    """
    prompt = _build_analysis_prompt(code, language, problem_id, problem_title, problem_type)
    c = client or _get_client()
    message = c.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_analysis_response(message.content[0].text.strip())


def build_chat_system_prompt(report: dict | None, language: str) -> str:
    if report:
        problem_id = report.get("challenge_id", "unknown")
        vuln_explanation = report.get("vulnerability_explanation") or report.get("explanation", "")
        attack_payload = report.get("attack_payload", "")
        problem_title = report.get("title", problem_id)
    else:
        problem_id = "unknown"
        language = language or "python"
        vuln_explanation = ""
        attack_payload = ""
        problem_title = "unknown"

    return (
        f"You are a security education assistant for SecureCraft, a secure coding education platform.\n"
        f"The student just completed the {problem_id} challenge in {language}.\n"
        f"Their submitted code had this vulnerability: {vuln_explanation}\n"
        f"The attack payload used was: {attack_payload}\n"
        f"Your role is to help them deeply understand the security concepts behind this challenge.\n"
        f"Keep responses concise, educational, and encouraging.\n"
        f"Use code examples when helpful. Respond in the same language the student uses."
    )


def chat_with_ai(
    system_prompt: str,
    history: list,
    user_message: str,
    client: anthropic.Anthropic | None = None,
) -> str:
    """
    Returns assistant reply text. Raises on API/network error — callers should catch.
    """
    messages = [*history, {"role": "user", "content": user_message}]
    c = client or _get_client()
    message = c.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=system_prompt,
        messages=messages,
    )
    return message.content[0].text
