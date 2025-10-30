# Single-stage build for WhatsApp Connect Service
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Runtime defaults (can be overridden by Coolify / env vars)
ENV PORT=8765 \
    GUNICORN_WORKERS=4 \
    GUNICORN_LOG_LEVEL=info

# Expose default port for documentation purposes
EXPOSE 8765

# Health check (respects dynamic PORT value)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD-SHELL "curl -fsS http://127.0.0.1:${PORT:-8765}/health || exit 1"

# Run with gunicorn for production, binding to the configured PORT
CMD ["sh", "-c", "exec gunicorn src.main:app --workers ${GUNICORN_WORKERS:-4} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8765} --access-logfile - --error-logfile - --log-level ${GUNICORN_LOG_LEVEL:-info}"]
