# scripts/run_tests_in_container.sh
#!/bin/bash

echo "=== Запуск тестов в контейнере ==="

docker build -t fastapi-app:test .

echo "Запуск тестов..."
docker run --rm \
    -e APP_ENV=test \
    fastapi-app:test \
    pytest tests/ -v --tb=short

echo "=== Тесты завершены ==="
