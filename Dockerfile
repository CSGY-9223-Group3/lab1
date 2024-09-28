# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster as builder

# Create a non-root user for enhanced security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Start a new stage for a smaller final image
FROM python:3.8-slim-buster

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