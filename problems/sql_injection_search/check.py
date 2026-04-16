import os, sys
output = os.getenv("ATTACK_OUTPUT", "")
if "API_KEY_12345" in output:
    print("FAIL: UNION injection extracted secrets from the database.")
    sys.exit(1)
else:
    print("PASS: UNION injection was blocked.")
    sys.exit(0)
