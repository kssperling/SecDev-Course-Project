#!/bin/bash
set -e

echo "=== Форматирование кода ==="

# Ruff форматирование
echo "1. Ruff форматирование..."
ruff format .

# Black форматирование
echo "2. Black форматирование..."
black .

# Isort сортировка импортов
echo "3. Isort сортировка импортов..."
isort .

# Ruff linting с исправлениями
echo "4. Ruff линтинг с исправлениями..."
ruff check --fix .

echo "✅ Форматирование завершено"
