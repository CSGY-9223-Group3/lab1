# Stage 1: Builder
FROM python:3.8-slim-buster AS builder

# Create a non-root user for enhanced security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final Image
FROM python:3.8-slim-buster

# Create a non-root user in the final image
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed dependencies and app from builder stage
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app
WORKDIR /app
COPY . .

# Set filesystem permissions for security
RUN chmod -R a-w /usr/local/lib/python3.8 && \
    chmod -R a-w /usr/local/lib/python3.8/site-packages

# Switch to non-root user
USER appuser

# Run the application
CMD ["python", "pastebin.py"]

# Note: This Dockerfile implements several security measures.
# For full details on security practices, please refer to SECURITY.md
# and the project documentation.
