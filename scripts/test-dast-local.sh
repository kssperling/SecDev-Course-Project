#!/bin/bash
set -e

echo "=== Local DAST Testing with OWASP ZAP ==="

# 1. Проверка зависимостей
echo "1. Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed."; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "curl is required but not installed."; exit 1; }

# 2. Запуск приложения
echo "2. Starting FastAPI application..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8080 > app.log 2>&1 &
APP_PID=$!

# 3. Ожидание запуска
echo "3. Waiting for application to start..."
sleep 5
for i in {1..10}; do
    if curl -s http://localhost:8080/health >/dev/null; then
        echo "✅ Application is running!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Failed to start application"
        cat app.log
        kill $APP_PID 2>/dev/null || true
        exit 1
    fi
    sleep 2
done

# 4. Создание директории для отчетов
echo "4. Creating evidence directory..."
mkdir -p EVIDENCE/P11

# 5. Запуск ZAP baseline сканирования
echo "5. Running OWASP ZAP baseline scan..."
docker run --rm \
    --network host \
    -v $(pwd)/EVIDENCE/P11:/zap/wrk/:rw \
    owasp/zap2docker-stable:latest \
    zap-baseline.py \
    -t "http://localhost:8080" \
    -r "zap_baseline.html" \
    -J "zap_baseline.json" \
    -a \
    -I \
    -j \
    -m 15

# 6. Остановка приложения
echo "6. Stopping application..."
kill $APP_PID 2>/dev/null || true

# 7. Генерация сводки
echo "7. Generating summary..."
if [ -f EVIDENCE/P11/zap_baseline.json ]; then
    echo "=== Scan Results ==="
    python3 -c "
import json
import os

report_path = 'EVIDENCE/P11/zap_baseline.json'
if os.path.exists(report_path):
    with open(report_path, 'r') as f:
        data = json.load(f)

    severity_map = {'3': 'High', '2': 'Medium', '1': 'Low', '0': 'Informational'}
    alerts_by_severity = {}

    if 'site' in data:
        for site in data['site']:
            for alert in site.get('alerts', []):
                risk = severity_map.get(str(alert.get('riskcode', '')), 'Unknown')
                alerts_by_severity[risk] = alerts_by_severity.get(risk, 0) + 1

    print('Alerts by severity:')
    for severity, count in alerts_by_severity.items():
        print(f'  {severity}: {count}')

    total = sum(alerts_by_severity.values())
    print(f'Total alerts: {total}')
else:
    print('No report generated')
"
else
    echo "No ZAP report generated"
fi

echo "=== Local DAST testing completed ==="
echo "Reports saved to: EVIDENCE/P11/"
ls -la EVIDENCE/P11/
