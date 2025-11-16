# Dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Создаем wheels (скомпилированные пакеты)
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Финальный образ
FROM python:3.11-slim as runtime

# Переменные окружения для безопасности
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Создаем non-root пользователя
RUN groupadd -r app && useradd -r -g app app

# Устанавливаем curl для healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

# Копируем wheels из builder
COPY --from=builder --chown=app:app /wheels /wheels

# Устанавливаем зависимости
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Копируем код приложения
COPY --chown=app:app . .

# Меняем пользователя
USER app

# Healthcheck (обязательно по критериям)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
