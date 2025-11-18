# scripts/check_container.sh
#!/bin/bash

echo "=== Проверка контейнеризации ==="

# Проверка сборки
echo "1. Сборка образа..."
docker build -t fastapi-app:test .

# Проверка размера
echo "2. Размер образа:"
docker images fastapi-app:test --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Проверка пользователя
echo "3. Проверка non-root пользователя:"
docker run --rm fastapi-app:test id -u

# Проверка healthcheck
echo "4. Запуск контейнера для проверки healthcheck..."
docker run -d --name health-test -p 8000:8000 fastapi-app:test

echo "Ожидание запуска..."
sleep 15

echo "5. Статус healthcheck:"
docker inspect --format='{{.State.Health.Status}}' health-test

echo "6. Проверка доступности приложения:"
curl -f http://localhost:8000/health || echo "Приложение недоступно"

# Очистка
docker stop health-test
docker rm health-test

echo "=== Проверка завершена ==="
