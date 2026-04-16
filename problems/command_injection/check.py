import os, sys

output = os.getenv("ATTACK_OUTPUT", "")

# attack.sh injects "127.0.0.1; id" and emits RESULT: VULNERABLE when the
# shell's id output (containing "uid=") appears in the ping response.
if "RESULT: VULNERABLE" in output or "uid=" in output:
    print("FAIL: Command injection succeeded — shell command output found in response.")
    sys.exit(1)
else:
    print("PASS: Command injection was blocked.")
    sys.exit(0)
