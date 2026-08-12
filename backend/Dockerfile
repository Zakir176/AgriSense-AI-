# ── AgriSense AI Backend ─────────────────────────────
# Multi-stage build: slim Python image with optional CV deps
# ─────────────────────────────────────────────────────

FROM python:3.12-slim AS base

# Prevent Python from writing .pyc and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies required by psycopg2-binary and librosa/opencv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        libsndfile1 \
        libgl1 \
        libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-full.txt ./
RUN pip install --no-cache-dir -r requirements-full.txt

# Copy application source
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
