import os, sys
output = os.getenv("ATTACK_OUTPUT", "")
if "root:" in output or "/bin/bash" in output:
    print("FAIL: Path traversal succeeded — /etc/passwd was read.")
    sys.exit(1)
else:
    print("PASS: Path traversal was blocked.")
    sys.exit(0)
