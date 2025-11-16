# Dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .

# hadolint ignore=DL3013,DL3042
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.11-slim as runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN groupadd -r app && useradd -r -g app app

COPY --from=builder --chown=app:app /wheels /wheels

# hadolint ignore=DL3042
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

COPY --chown=app:app . .

USER app

# Простой healthcheck на Python (без curl)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
