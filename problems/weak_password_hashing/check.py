import os, sys
output = os.getenv("ATTACK_OUTPUT", "")
if "DETECTED: Hash is MD5 format" in output:
    print("FAIL: Passwords are still hashed with MD5.")
    sys.exit(1)
else:
    print("PASS: Passwords use a strong hashing algorithm (bcrypt or similar).")
    sys.exit(0)
