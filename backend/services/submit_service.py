import os
import re

from ai_analyzer import analyze_code_with_ai

EXT_MAP = {"python": "py", "php": "php", "java": "java"}


def find_vuln_lines(code: str, patterns: list) -> list:
    matched = []
    for i, line in enumerate(code.splitlines(), start=1):
        for pattern in patterns:
            if re.search(pattern, line):
                matched.append(i)
                break
    return matched


def assemble_report(
    session_id: str,
    challenge_id: str,
    code: str,
    language: str,
    meta: dict,
    validation_result: dict,
    problems_dir: str,
) -> dict:
    ext = EXT_MAP.get(language, "py")
    solution_path = os.path.join(problems_dir, challenge_id, f"solution_{language}.{ext}")
    fixed_code = ""
    if os.path.exists(solution_path):
        with open(solution_path) as fh:
            fixed_code = fh.read()

    lang_patterns = meta.get("vuln_patterns", {})
    patterns = lang_patterns.get(language, []) if isinstance(lang_patterns, dict) else lang_patterns
    regex_vuln_lines = find_vuln_lines(code, patterns)

    ai_analysis = None
    ai_error = None
    try:
        ai_analysis = analyze_code_with_ai(
            code=code,
            language=language,
            problem_id=challenge_id,
            problem_title=meta.get("title", challenge_id),
            problem_type=challenge_id,
        )
    except Exception as exc:
        ai_error = str(exc)

    if ai_analysis:
        ai_vuln_lines = ai_analysis.get("vuln_lines") or []
        final_vuln_lines = ai_vuln_lines if ai_vuln_lines else regex_vuln_lines
    else:
        final_vuln_lines = regex_vuln_lines

    report = dict(validation_result)
    report.update({
        "session_id": session_id,
        "challenge_id": challenge_id,
        "title": meta.get("title", challenge_id),
        "canonical_fix": meta.get("canonical_fix", ""),
        "explanation": meta.get("explanation", ""),
        "why_blocked": meta.get("why_blocked", ""),
        "submitted_code": code,
        "fixed_code": fixed_code,
        "vulnerable_lines": final_vuln_lines,
        "attack_payload": meta.get("attack_payload", ""),
        "attack_flow": meta.get("attack_flow", []),
        "vulnerability_explanation": ai_analysis.get("vulnerability_explanation") if ai_analysis else None,
        "fix_hint": ai_analysis.get("fix_hint") if ai_analysis else None,
        "severity": ai_analysis.get("severity") if ai_analysis else None,
        "ai_analysis": ai_analysis,
        "ai_error": ai_error,
    })
    return report
