FROM eclipse-temurin:21-jdk-alpine
WORKDIR /app

# Install runtime utilities
RUN apk add --no-cache bash curl wget

# Pre-download JAR dependencies so the image is self-contained
RUN mkdir -p /app/lib && \
    wget -q --timeout=30 --tries=2 https://repo1.maven.org/maven2/org/json/json/20240303/json-20240303.jar \
         -O /app/lib/json.jar && \
    wget -q --timeout=30 --tries=2 https://repo1.maven.org/maven2/org/xerial/sqlite-jdbc/3.45.3.0/sqlite-jdbc-3.45.3.0.jar \
         -O /app/lib/sqlite-jdbc.jar

# Copy challenge support files (attack.sh, check.py, templates/, etc.)
# solution.java is injected at runtime by the orchestrator
COPY attack.sh check.py /app/
COPY templates/ /app/templates/
COPY skeleton_java.java /app/skeleton_java.java
RUN chmod +x /app/attack.sh

# At runtime: compile and run the injected solution.java
CMD ["sh", "-c", "javac -cp '/app/lib/*' /app/skeleton_java.java && java -cp '/app:/app/lib/*' skeleton_java & sleep infinity"]
