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
    -d '{}' \
    | grep -qE "^[0-9]" && break
  sleep 0.5
done

# Send 10 rapid login attempts and check if any return 429
GOT_429=0
for i in $(seq 1 10); do
  STATUS=$(post_status "http://localhost:8080/login" \
    '{"username":"admin","password":"wrong"}')
  echo "Attempt $i: HTTP $STATUS"
  if [ "$STATUS" = "429" ]; then
    GOT_429=1
  fi
done

if [ "$GOT_429" = "1" ]; then
  echo "RATE_LIMIT_ACTIVE"
else
  echo "NO_RATE_LIMIT"
fi
