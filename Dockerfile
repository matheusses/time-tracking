# Multi-stage Dockerfile for time-tracking Django app
# Stage 1: builder (deps, optional static/tooling)
FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: final (slim runtime, non-root)
FROM python:3.12-slim as runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=project.settings

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos "" appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

# Default: run gunicorn; override in compose for runserver/shell
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
