# Build stage
FROM python:3.11-slim AS build
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
COPY . .
RUN pytest -q

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
RUN useradd -m appuser
COPY --from=build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
USER appuser
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



# Dockerfile
# syntax=docker/dockerfile:1.4
FROM python:3.11-slim as builder

WORKDIR /app

# Устанавливаем системные зависимости только для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Создаем wheels
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Финальный образ
FROM python:3.11-slim as runtime

# Переменные окружения для безопасности
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Создаем non-root пользователя
RUN groupadd -r app && useradd -r -g app app

# Устанавливаем только необходимые системные пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Копируем wheels из builder
COPY --from=builder --chown=app:app /wheels /wheels

# Устанавливаем зависимости
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Копируем код приложения
COPY --chown=app:app . .

# Меняем пользователя
USER app

# Healthcheck для FastAPI
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
