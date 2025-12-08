# Makefile
.PHONY: build run test scan lint clean

# Сборка образа
build:
	docker build -t fastapi-app:latest .

# Запуск приложения
run:
	docker-compose up app

# Запуск тестов
test:
	docker-compose run --rm tests

# Сканирование образа на уязвимости
scan:
	docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy:latest image fastapi-app:latest

# Линтинг Dockerfile
lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

# Проверка безопасности контейнера
security-check:
	@echo "=== Проверка пользователя в контейнере ==="
	docker run --rm fastapi-app:latest id -u
	@echo "=== Проверка healthcheck ==="
	docker run -d --name test-container -p 8000:8000 fastapi-app:latest
	sleep 10
	docker inspect --format='{{.State.Health.Status}}' test-container
	docker stop test-container
	docker rm test-container

# Очистка
clean:
	docker-compose down
	docker system prune -f

all: build lint scan security-check
