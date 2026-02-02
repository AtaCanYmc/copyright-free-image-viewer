# Build stage  — eğer frontend vs. varsa burada topla
FROM python:3.10-slim AS base

# metadata
LABEL org.opencontainers.image.authors="AtaCanYmc"
LABEL org.opencontainers.image.url="https://github.com/AtaCanYmc/copyright-free-image-viewer"
LABEL org.opencontainers.image.description="Flask based copyright free image search & management UI"
LABEL org.opencontainers.image.license="MIT"
LABEL org.opencontainers.image.version="1.0.0"

# Set working directory
WORKDIR /app

# System deps (flask + Pillow dependencies)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# non-root user
RUN addgroup --system app && adduser --system --ingroup app app
USER root

# Config port from env if provided
EXPOSE 8080

# Health check (Flask health endpoint, if implemented)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD curl -fs http://localhost:8080/health || exit 1

# Entrypoint
ENTRYPOINT ["python", "app.py"]
