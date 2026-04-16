FROM php:8.2-cli
WORKDIR /app

# Install PDO SQLite extension + curl
RUN apt-get update && apt-get install -y curl python3 --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy challenge support files
# solution.php is injected at runtime by the orchestrator
COPY attack.sh check.py /app/
COPY templates/ /app/templates/
COPY solution.php /app/solution.php
RUN chmod +x /app/attack.sh

# At runtime: serve the injected solution.php via PHP built-in web server
CMD ["sh", "-c", "php -S 0.0.0.0:8080 /app/solution.php"]
