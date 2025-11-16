# Makefile
.PHONY: build run test scan lint clean

build:
	docker build -t fastapi-app .

run:
	docker-compose up app

test:
	docker-compose run --rm app python -c "import app.main; print('✅ App imports work')"

scan:
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image fastapi-app

lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

security-check:
	@echo "=== Checking non-root user ==="
	@docker run --rm fastapi-app id -u | grep -v '^0$$' && echo "✅ Non-root user" || echo "❌ Root user"
	@echo "=== Checking healthcheck ==="
	@docker run -d --name health-test fastapi-app
	@sleep 10
	@docker inspect --format='{{.State.Health.Status}}' health-test | grep -E '(healthy|starting)' && echo "✅ Healthcheck working" || echo "❌ Healthcheck failed"
	@docker stop health-test
	@docker rm health-test

clean:
	docker-compose down
	docker system prune -f

all: build lint security-check
