#!/bin/bash
# Wait for Flask to be ready
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:8080/register \
    -H "Content-Type: application/json" \
    -d '{"username":"probe","password":"probe"}' \
    | grep -qE "^[0-9]" && break
  sleep 0.5
done

# Register a user whose hash we will leak
curl -s -o /dev/null \
  -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"password123"}'

# Leak the hash (simulate DB breach)
HASH_RESPONSE=$(curl -s "http://localhost:8080/hash?user=alice")
HASH=$(echo "$HASH_RESPONSE" | grep -o '"hash":"[^"]*"' | cut -d'"' -f4)

echo "Leaked hash: $HASH"

# Check if it looks like MD5 (32 hex chars)
if echo "$HASH" | grep -qE '^[a-f0-9]{32}$'; then
  echo "DETECTED: Hash is MD5 format"
else
  echo "Hash appears to use a stronger algorithm"
fi
