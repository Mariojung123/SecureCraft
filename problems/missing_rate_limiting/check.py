import os, sys
output = os.getenv("ATTACK_OUTPUT", "")
if "RATE_LIMIT_ACTIVE" in output:
    print("PASS: Rate limiting is active — brute-force was throttled.")
    sys.exit(0)
else:
    print("FAIL: No rate limiting detected — all 10 attempts returned 401, not 429.")
    sys.exit(1)
