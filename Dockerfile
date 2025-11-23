# Magnus Trading Platform - Production Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Base Python image with dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional production dependencies
RUN pip install --no-cache-dir \
    gunicorn==21.2.0 \
    celery==5.3.4 \
    redis==5.0.1 \
    asyncpg==0.29.0

# Stage 3: Application
FROM dependencies as application

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p \
    /app/logs \
    /app/data \
    /app/models \
    /app/.streamlit

# Expose ports
EXPOSE 8501 5555

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Stage 4: Development image (with dev tools)
FROM application as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest==7.4.3 \
    pytest-cov==4.1.0 \
    black==23.12.0 \
    flake8==6.1.0 \
    mypy==1.7.1

# Expose debugging port
EXPOSE 5678

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave=true"]
