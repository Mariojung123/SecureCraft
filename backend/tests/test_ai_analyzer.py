import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_analyzer import _parse_analysis_response, build_chat_system_prompt


# ---------------------------------------------------------------------------
# _parse_analysis_response
# ---------------------------------------------------------------------------

class TestParseAnalysisResponse:
    def test_plain_json(self):
        raw = '{"vuln_lines": [3], "severity": "HIGH", "is_vulnerable": true}'
        result = _parse_analysis_response(raw)
        assert result["severity"] == "HIGH"
        assert result["vuln_lines"] == [3]

    def test_markdown_fence_json(self):
        raw = "```json\n{\"vuln_lines\": [5], \"severity\": \"LOW\"}\n```"
        result = _parse_analysis_response(raw)
        assert result["severity"] == "LOW"
        assert result["vuln_lines"] == [5]

    def test_markdown_fence_no_lang(self):
        raw = "```\n{\"vuln_lines\": [], \"severity\": \"NONE\"}\n```"
        result = _parse_analysis_response(raw)
        assert result["severity"] == "NONE"

    def test_whitespace_trimmed(self):
        raw = '  \n{"vuln_lines": [1], "severity": "MEDIUM"}\n  '
        result = _parse_analysis_response(raw)
        assert result["severity"] == "MEDIUM"

    def test_invalid_json_raises(self):
        with pytest.raises(Exception):
            _parse_analysis_response("not json at all")

    def test_all_fields_present(self):
        raw = '{"vuln_lines": [2, 4], "severity": "HIGH", "vulnerability_explanation": "SQL injection", "fix_hint": "Use parameterized queries", "is_vulnerable": true}'
        result = _parse_analysis_response(raw)
        assert result["is_vulnerable"] is True
        assert result["fix_hint"] == "Use parameterized queries"
        assert result["vulnerability_explanation"] == "SQL injection"


# ---------------------------------------------------------------------------
# build_chat_system_prompt
# ---------------------------------------------------------------------------

class TestBuildChatSystemPrompt:
    def test_with_full_report(self):
        report = {
            "challenge_id": "sql_injection_login",
            "title": "SQL Injection Login",
            "vulnerability_explanation": "Unsanitized input passed to query",
            "attack_payload": "' OR '1'='1",
        }
        prompt = build_chat_system_prompt(report, "python")
        assert "sql_injection_login" in prompt
        assert "python" in prompt
        assert "Unsanitized input" in prompt
        assert "' OR '1'='1" in prompt

    def test_with_none_report(self):
        prompt = build_chat_system_prompt(None, "python")
        assert "unknown" in prompt
        assert "python" in prompt

    def test_report_missing_optional_fields(self):
        report = {"challenge_id": "xss_reflected"}
        prompt = build_chat_system_prompt(report, "php")
        assert "xss_reflected" in prompt
        assert "php" in prompt

    def test_report_uses_explanation_fallback(self):
        # vulnerability_explanation absent → falls back to explanation field
        report = {
            "challenge_id": "path_traversal",
            "title": "Path Traversal",
            "explanation": "Path not sanitized",
            "attack_payload": "../etc/passwd",
        }
        prompt = build_chat_system_prompt(report, "python")
        assert "Path not sanitized" in prompt

    def test_language_in_prompt(self):
        prompt = build_chat_system_prompt(None, "java")
        assert "java" in prompt
