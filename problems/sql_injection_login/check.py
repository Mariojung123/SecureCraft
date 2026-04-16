"""
Exit 0 = fix is correct (attack failed, vulnerability patched).
Exit 1 = still vulnerable (attack succeeded).
"""
import os
import sys

output = os.getenv("ATTACK_OUTPUT", "")

# attack.sh prints "RESULT: VULNERABLE" when any injection payload got HTTP 200
# and "RESULT: SAFE" when all payloads were rejected.
if "RESULT: VULNERABLE" in output:
    print("FAIL: SQL injection bypass succeeded — the vulnerability is still present.")
    sys.exit(1)
else:
    print("PASS: SQL injection bypass was blocked — the fix looks correct.")
    sys.exit(0)
