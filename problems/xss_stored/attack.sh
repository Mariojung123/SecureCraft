#!/bin/bash
# Wait for Flask to be ready
for i in $(seq 1 15); do
  curl -s -o /dev/null "http://localhost:8080/" && break
  sleep 0.5
done

# Post a stored XSS payload via JSON
curl -s -o /dev/null \
  -X POST http://localhost:8080/comment \
  -H "Content-Type: application/json" \
  -d '{"body":"<script>alert('"'"'xss'"'"')</script>"}' > /dev/null 2>&1

# Fetch the page and check if the payload was stored unescaped
RESPONSE=$(curl -s "http://localhost:8080/")
echo "Response: $RESPONSE"
