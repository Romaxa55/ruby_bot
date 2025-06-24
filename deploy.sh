#!/bin/bash

# Ruby Bot Deployment Script
# Загружает переменные окружения из .env и деплоит в Kubernetes

set -e

echo "🚀 Запуск деплоя Ruby Bot..."

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден! Создайте его на основе .env.example"
    exit 1
fi

# Загружаем переменные из .env
echo "📋 Загружаем переменные окружения из .env..."
export $(grep -v '^#' .env | xargs)

# Проверяем обязательные переменные
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN не установлен в .env"
    exit 1
fi

if [ -z "$MTPROXY_SECRET" ]; then
    echo "❌ MTPROXY_SECRET не установлен в .env"
    exit 1
fi

echo "✅ Переменные окружения загружены"

# Создаем namespace если не существует
echo "🔧 Создание namespace..."
kubectl create namespace ruby-bot --dry-run=client -o yaml | kubectl apply -f -

# Создаем секреты
echo "🔐 Создание Kubernetes секретов..."
kubectl create secret generic bot-token \
    --from-literal=token="$BOT_TOKEN" \
    --namespace=ruby-bot \
    --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic mtproxy-secret \
    --from-literal=secret="$MTPROXY_SECRET" \
    --namespace=ruby-bot \
    --dry-run=client -o yaml | kubectl apply -f -

# Деплой через Helm
echo "⚙️ Деплой через Helm..."
helm upgrade --install ruby-bot ./ruby-bot \
    --namespace=ruby-bot \
    --set image.tag=latest \
    --set replicaCount=1

echo "✅ Деплой завершен!"
echo "📊 Проверка статуса подов:"
kubectl get pods -n ruby-bot

echo ""
echo "📋 Полезные команды:"
echo "  kubectl logs -f deployment/ruby-bot -n ruby-bot  # Логи"
echo "  kubectl get pods -n ruby-bot                     # Статус подов"
echo "  kubectl describe pod <pod-name> -n ruby-bot      # Детали пода" 