import os
import re
import threading

import sandbox.orchestrator as orchestrator
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


def read_skeleton(problems_dir: str, challenge_id: str, language: str) -> str:
    ext = EXT_MAP.get(language, "py")
    path = os.path.join(problems_dir, challenge_id, f"skeleton_{language}.{ext}")
    if not os.path.exists(path):
        return ""
    with open(path) as fh:
        return fh.read()


def _read_solution(problems_dir: str, challenge_id: str, language: str) -> str:
    ext = EXT_MAP.get(language, "py")
    path = os.path.join(problems_dir, challenge_id, f"solution_{language}.{ext}")
    if not os.path.exists(path):
        return ""
    with open(path) as fh:
        return fh.read()


def _get_regex_vuln_lines(code: str, meta: dict, language: str) -> list:
    lang_patterns = meta.get("vuln_patterns", {})
    patterns = lang_patterns.get(language, []) if isinstance(lang_patterns, dict) else lang_patterns
    return find_vuln_lines(code, patterns)


def _get_ai_analysis(code: str, language: str, meta: dict, challenge_id: str) -> tuple:
    try:
        result = analyze_code_with_ai(
            code=code,
            language=language,
            problem_id=challenge_id,
            problem_title=meta.get("title", challenge_id),
            problem_type=challenge_id,
        )
        return result, None
    except Exception as exc:
        return None, str(exc)


def _resolve_vuln_lines(ai_analysis: dict | None, regex_vuln_lines: list) -> list:
    if not ai_analysis:
        return regex_vuln_lines
    ai_lines = ai_analysis.get("vuln_lines") or []
    return ai_lines if ai_lines else regex_vuln_lines


def _make_updater(session_id: str, sessions: dict, sessions_lock: threading.Lock):
    def update(**kwargs):
        with sessions_lock:
            if session_id in sessions:
                sessions[session_id].update(kwargs)
    return update


def _run_concurrent(fn1, fn2, name1: str, name2: str) -> None:
    t1 = threading.Thread(target=fn1, daemon=True, name=name1)
    t2 = threading.Thread(target=fn2, daemon=True, name=name2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def assemble_report(
    session_id: str,
    challenge_id: str,
    code: str,
    language: str,
    meta: dict,
    validation_result: dict,
    problems_dir: str,
) -> dict:
    fixed_code = _read_solution(problems_dir, challenge_id, language)
    regex_vuln_lines = _get_regex_vuln_lines(code, meta, language)
    ai_analysis, ai_error = _get_ai_analysis(code, language, meta, challenge_id)
    final_vuln_lines = _resolve_vuln_lines(ai_analysis, regex_vuln_lines)

    report = dict(validation_result)
    report.update({
        "session_id": session_id,
        "challenge_id": challenge_id,
        "language": language,
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


def run_submit_pipeline(
    session_id: str,
    challenge_id: str,
    code: str,
    language: str,
    meta: dict,
    sessions: dict,
    sessions_lock: threading.Lock,
    problems_dir: str,
) -> None:
    """Background coordinator: build image → validate + sandbox concurrently."""
    update = _make_updater(session_id, sessions, sessions_lock)

    try:
        image_tag = orchestrator.build_image(challenge_id, code, language)
    except Exception as exc:
        update(status="error", error=f"Image build failed: {exc}")
        return

    def validation():
        result = orchestrator.run_validation(challenge_id, image_tag, language)
        report = assemble_report(
            session_id=session_id, challenge_id=challenge_id, code=code,
            language=language, meta=meta, validation_result=result, problems_dir=problems_dir,
        )
        update(report=report, status="done")

    def sandbox():
        try:
            container_id, port = orchestrator.run_sandbox(image_tag, session_id, language)
            update(container_id=container_id, port=port)
        except Exception as exc:
            update(error=f"Sandbox error: {exc}")

    _run_concurrent(
        validation, sandbox,
        f"validate-{session_id[:8]}", f"sandbox-{session_id[:8]}",
    )
