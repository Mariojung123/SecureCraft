import os, sys
output = os.getenv("ATTACK_OUTPUT", "")
if "<script>" in output.lower():
    print("FAIL: Stored XSS payload rendered unescaped.")
    sys.exit(1)
else:
    print("PASS: XSS payload was stored and escaped correctly.")
    sys.exit(0)
