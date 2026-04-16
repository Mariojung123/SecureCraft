#!/bin/bash
# Wait for Flask to be ready
for i in $(seq 1 15); do
  curl -s -o /dev/null "http://localhost:8080/search?q=test" && break
  sleep 0.5
done

# Inject a <script> tag via the query parameter
RESPONSE=$(curl -s "http://localhost:8080/search?q=%3Cscript%3Ealert%281%29%3C%2Fscript%3E")
echo "Response: $RESPONSE"
