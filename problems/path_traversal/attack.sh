#!/bin/bash
# Wait for Flask to be ready
for i in $(seq 1 15); do
  curl -s -o /dev/null "http://localhost:8080/download?file=public.txt" && break
  sleep 0.5
done

# Attempt to escape the base directory with a path traversal payload
RESPONSE=$(curl -s "http://localhost:8080/download?file=..%2F..%2Fetc%2Fpasswd")
echo "Response: $RESPONSE"
