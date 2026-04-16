#!/bin/bash
# Helper: POST JSON to URL, print HTTP status code
post_status() {
  # Usage: post_status <url> <json_body>
  curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$1" \
    -H "Content-Type: application/json" \
    -d "$2"
}

# Wait for the Flask app to be ready
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:8080/login \
    -H "Content-Type: application/json" \
    -d '{"username":"","password":""}' \
    | grep -qE "^[0-9]" && break
  sleep 0.5
done

VULNERABLE=0

# ── Payload 1: classic OR bypass ────────────────────────────────────────────
STATUS=$(post_status "http://localhost:8080/login" \
  '{"username":"'"'"' OR '"'"'1'"'"'='"'"'1'"'"' --","password":"anything"}')
echo "Payload 1 (' OR '1'='1' --): HTTP $STATUS"
[ "$STATUS" = "200" ] && VULNERABLE=1

# ── Payload 2: comment-based bypass ─────────────────────────────────────────
STATUS=$(post_status "http://localhost:8080/login" \
  '{"username":"admin'"'"'--","password":"wrong"}')
echo "Payload 2 (admin'--): HTTP $STATUS"
[ "$STATUS" = "200" ] && VULNERABLE=1

# ── Payload 3: always-true with known username ───────────────────────────────
STATUS=$(post_status "http://localhost:8080/login" \
  '{"username":"admin'"'"' OR 1=1--","password":"x"}')
echo "Payload 3 (admin' OR 1=1--): HTTP $STATUS"
[ "$STATUS" = "200" ] && VULNERABLE=1

# ── Sanity check: correct credentials must still work ────────────────────────
STATUS=$(post_status "http://localhost:8080/login" \
  '{"username":"admin","password":"supersecret123"}')
echo "Sanity check (valid login): HTTP $STATUS"
[ "$STATUS" != "200" ] && echo "WARNING: valid credentials were rejected — check your implementation" && VULNERABLE=1

# ── Result ───────────────────────────────────────────────────────────────────
if [ "$VULNERABLE" = "1" ]; then
  echo "RESULT: VULNERABLE"
  exit 1
else
  echo "RESULT: SAFE"
  exit 0
fi
