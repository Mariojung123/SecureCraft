#!/bin/bash
# Wait for Flask to be ready
for i in $(seq 1 15); do
  curl -s -o /dev/null "http://localhost:8080/ping?host=localhost" && break
  sleep 0.5
done

# Inject semicolon + id command to test for command injection
RESPONSE=$(curl -s "http://localhost:8080/ping?host=127.0.0.1%3B%20id")
echo "Response: $RESPONSE"

# Check if injection succeeded (uid= appears in shell command output)
if echo "$RESPONSE" | grep -q 'uid='; then
  echo "RESULT: VULNERABLE — command injection succeeded (uid= found in output)"
else
  echo "RESULT: SAFE — no command injection detected"
fi
