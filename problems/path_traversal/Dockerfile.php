FROM php:8.2-cli
WORKDIR /app
RUN apt-get update && apt-get install -y curl python3 --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
COPY attack.sh check.py /app/
COPY templates/ /app/templates/
COPY solution.php /app/solution.php
RUN chmod +x /app/attack.sh
CMD ["sh", "-c", "php -S 0.0.0.0:8080 /app/solution.php"]
