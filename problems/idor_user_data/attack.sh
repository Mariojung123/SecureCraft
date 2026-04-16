#!/bin/bash
# Wait for Flask to be ready
for i in $(seq 1 15); do
  curl -s -o /dev/null -H "X-User-Id: 1" "http://localhost:8080/profile/1" && break
  sleep 0.5
done

# Attacker is user 1, trying to read user 2's profile
BODY=$(curl -s -H "X-User-Id: 1" "http://localhost:8080/profile/2")
echo "Response: $BODY"
