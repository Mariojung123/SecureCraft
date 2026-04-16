import os, sys
output = os.getenv("ATTACK_OUTPUT", "")
if "<script>" in output.lower():
    print("FAIL: XSS payload was reflected unescaped in the response.")
    sys.exit(1)
else:
    print("PASS: XSS payload was escaped correctly.")
    sys.exit(0)
