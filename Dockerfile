# Multi-stage build for optimal size and caching
FROM python:3.11-slim-bullseye as base

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user for security
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Create directories and set ownership
RUN mkdir -p /app/data /app/logs && chown -R app:app /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage with hot reloading
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir watchdog[watchmedo] uvicorn[standard]

# Switch to app user (directories already created and owned by app)
USER app

# Expose port
EXPOSE 8000

# Development command with hot reloading
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]

# Production stage (for future use)
FROM base as production

# Copy application code
COPY --chown=app:app . .

# Switch to app user (directories already created in base stage)
USER app

# Expose port
EXPOSE 8000

# Production command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]