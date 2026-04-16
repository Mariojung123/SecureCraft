import os, sys
output = os.getenv("ATTACK_OUTPUT", "")
if "987-65-4321" in output or "bob@example.com" in output:
    print("FAIL: IDOR succeeded — user 1 read user 2's private data.")
    sys.exit(1)
else:
    print("PASS: IDOR blocked — cross-user access was denied.")
    sys.exit(0)
