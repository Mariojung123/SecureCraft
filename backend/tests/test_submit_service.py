import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services"))

from services.submit_service import (
    _get_regex_vuln_lines,
    _resolve_vuln_lines,
    find_vuln_lines,
    read_skeleton,
)


# ---------------------------------------------------------------------------
# find_vuln_lines
# ---------------------------------------------------------------------------

class TestFindVulnLines:
    def test_single_pattern_match(self):
        code = "x = eval(user_input)\ny = 1"
        assert find_vuln_lines(code, [r"eval\("]) == [1]

    def test_multiple_lines_match(self):
        code = "a = eval(x)\nb = safe()\nc = eval(y)"
        assert find_vuln_lines(code, [r"eval\("]) == [1, 3]

    def test_no_match(self):
        code = "x = int(user_input)"
        assert find_vuln_lines(code, [r"eval\("]) == []

    def test_empty_patterns(self):
        code = "x = eval(y)"
        assert find_vuln_lines(code, []) == []

    def test_empty_code(self):
        assert find_vuln_lines("", [r"eval\("]) == []

    def test_line_matched_once_per_line(self):
        # Two patterns both match same line — should appear only once
        code = "os.system(user_input)"
        result = find_vuln_lines(code, [r"os\.system", r"user_input"])
        assert result == [1]

    def test_multiline_correct_numbers(self):
        code = "safe_line\nos.system(cmd)\nanother_safe\neval(x)"
        assert find_vuln_lines(code, [r"os\.system", r"eval\("]) == [2, 4]


# ---------------------------------------------------------------------------
# _resolve_vuln_lines
# ---------------------------------------------------------------------------

class TestResolveVulnLines:
    def test_no_ai_returns_regex(self):
        assert _resolve_vuln_lines(None, [1, 2, 3]) == [1, 2, 3]

    def test_ai_lines_present_overrides_regex(self):
        ai = {"vuln_lines": [5, 6], "severity": "HIGH"}
        assert _resolve_vuln_lines(ai, [1, 2]) == [5, 6]

    def test_ai_empty_lines_fallback_to_regex(self):
        ai = {"vuln_lines": [], "severity": "LOW"}
        assert _resolve_vuln_lines(ai, [3, 4]) == [3, 4]

    def test_ai_none_lines_key_fallback(self):
        ai = {"vuln_lines": None, "severity": "MEDIUM"}
        assert _resolve_vuln_lines(ai, [7]) == [7]

    def test_ai_missing_lines_key_fallback(self):
        ai = {"severity": "HIGH"}
        assert _resolve_vuln_lines(ai, [2]) == [2]


# ---------------------------------------------------------------------------
# _get_regex_vuln_lines
# ---------------------------------------------------------------------------

class TestGetRegexVulnLines:
    def test_dict_patterns_correct_language(self):
        code = "cursor.execute(query)"
        meta = {"vuln_patterns": {"python": [r"execute\(query\)"], "php": []}}
        assert _get_regex_vuln_lines(code, meta, "python") == [1]

    def test_dict_patterns_wrong_language_no_match(self):
        code = "cursor.execute(query)"
        meta = {"vuln_patterns": {"python": [r"execute\(query\)"], "php": []}}
        assert _get_regex_vuln_lines(code, meta, "php") == []

    def test_list_patterns_legacy_format(self):
        code = "eval(user)"
        meta = {"vuln_patterns": [r"eval\("]}
        assert _get_regex_vuln_lines(code, meta, "python") == [1]

    def test_missing_vuln_patterns_key(self):
        code = "eval(user)"
        meta = {}
        assert _get_regex_vuln_lines(code, meta, "python") == []

    def test_language_not_in_dict(self):
        code = "eval(user)"
        meta = {"vuln_patterns": {"php": [r"eval\("]}}
        assert _get_regex_vuln_lines(code, meta, "python") == []


# ---------------------------------------------------------------------------
# read_skeleton
# ---------------------------------------------------------------------------

class TestReadSkeleton:
    def test_file_exists_returns_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            challenge_dir = os.path.join(tmpdir, "sql_injection")
            os.makedirs(challenge_dir)
            skeleton_path = os.path.join(challenge_dir, "skeleton_python.py")
            with open(skeleton_path, "w") as f:
                f.write("# vulnerable code\n")
            result = read_skeleton(tmpdir, "sql_injection", "python")
            assert result == "# vulnerable code\n"

    def test_file_missing_returns_empty_string(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = read_skeleton(tmpdir, "nonexistent", "python")
            assert result == ""

    def test_php_extension_resolved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            challenge_dir = os.path.join(tmpdir, "xss")
            os.makedirs(challenge_dir)
            skeleton_path = os.path.join(challenge_dir, "skeleton_php.php")
            with open(skeleton_path, "w") as f:
                f.write("<?php echo $_GET['x']; ?>")
            result = read_skeleton(tmpdir, "xss", "php")
            assert result == "<?php echo $_GET['x']; ?>"

    def test_unknown_language_defaults_to_py_extension(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            challenge_dir = os.path.join(tmpdir, "test_challenge")
            os.makedirs(challenge_dir)
            skeleton_path = os.path.join(challenge_dir, "skeleton_cobol.py")
            with open(skeleton_path, "w") as f:
                f.write("code")
            result = read_skeleton(tmpdir, "test_challenge", "cobol")
            assert result == "code"
