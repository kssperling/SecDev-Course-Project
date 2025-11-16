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

# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

COPY --from=builder --chown=app:app /wheels /wheels

# hadolint ignore=DL3042
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

COPY --chown=app:app . .

USER app

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
