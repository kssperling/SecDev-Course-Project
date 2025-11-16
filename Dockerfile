# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости first для лучшего кэширования
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Создаем non-root пользователя (но не переключаемся пока)
RUN groupadd -r app && useradd -r -g app app

# Даем права на запись в рабочую директорию
RUN chown -R app:app /app

# Переключаемся на non-root пользователя
USER app

# Простая команда для проверки
CMD ["python", "-c", "print('Container is working!'); import time; time.sleep(60)"]
