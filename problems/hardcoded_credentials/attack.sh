#!/bin/bash
# Wait for Flask to be ready (any response from /admin, even 403, means it's up)
for i in $(seq 1 15); do
  curl -s -o /dev/null "http://localhost:8080/admin" && break
  sleep 0.5
done

# Use the hardcoded key found in source
BODY=$(curl -s -H "X-Api-Key: super_secret_admin_key_1234" "http://localhost:8080/admin")
echo "Response: $BODY"
