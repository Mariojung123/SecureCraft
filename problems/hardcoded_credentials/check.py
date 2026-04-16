import os, sys
output = os.getenv("ATTACK_OUTPUT", "")
if "Sensitive admin data" in output:
    print("FAIL: Hardcoded key accepted — admin endpoint was accessed.")
    sys.exit(1)
else:
    print("PASS: Hardcoded key no longer works — secret is loaded from env.")
    sys.exit(0)
