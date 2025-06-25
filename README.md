# Ruby Bot 🤖

Ruby Bot - это Telegram бот для удаленного управления Android устройствами через ADB с поддержкой SOCKS5 прокси для обхода блокировок.

## Возможности

- 🔄 Управление ориентацией экрана (портрет/альбом)
- 🎥 Воспроизведение видео файлов
- 📱 Подключение к ADB устройствам
- 🌐 Поддержка SOCKS5 прокси для обхода блокировок Telegram
- 🔐 Безопасное управление секретами через переменные окружения
- ☸️ Готовность к развертыванию в Kubernetes

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/Romaxa55/ruby_bot.git
cd ruby_bot
```

### 2. Настройка окружения

```bash
# Создаем виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 3. Конфигурация

Создайте `.env` файл на основе примера:

```bash
cp .env.example .env
```

Заполните `.env` файл своими данными:

```bash
# Основные настройки
BOT_TOKEN=your_bot_token_here
ADB_DEVICE_IP=192.168.1.100
VIDEO_PATH=/storage/self/primary/video/spa_noaudio.mp4

# Прокси (опционально, для обхода блокировок)
TELEGRAM_PROXY_ENABLED=true
TELEGRAM_PROXY_URL=socks5://user:pass@host:port

# MTProxy (альтернативный способ обхода блокировок)
MTPROXY_HOST=t.segfault.net
MTPROXY_PORT=8443
MTPROXY_SECRET=bcfb182a1bafbc16ea92652628133c07
```

### 4. Запуск

```bash
python main.py
```

## Команды бота

- `/start` - Показать статус и конфигурацию
- `/check_proxy` - Проверить статус прокси
- `/set_landscape` - Установить альбомную ориентацию
- `/set_portrait` - Установить портретную ориентацию
- `/play_video` - Воспроизвести видео
- `/adb_connect` - Подключиться к ADB устройству

## Развертывание в Kubernetes

### Предварительные требования

- Kubernetes кластер
- Helm 3.x
- kubectl настроенный для работы с кластером

### Деплой

1. **Подготовка секретов**

   Убедитесь что `.env` файл заполнен правильными данными.

2. **Запуск деплоя**

   ```bash
   ./deploy.sh
   ```

   Скрипт автоматически:
   - Создаст namespace `ruby-bot`
   - Создаст Kubernetes секреты из `.env` файла
   - Развернет приложение через Helm

3. **Проверка статуса**

   ```bash
   kubectl get pods -n ruby-bot
   kubectl logs -f deployment/ruby-bot -n ruby-bot
   ```

## Структура проекта

```
ruby_bot/
├── main.py                 # Основной файл бота
├── requirements.txt        # Python зависимости
├── Dockerfile             # Docker образ
├── deploy.sh              # Скрипт деплоя в Kubernetes
├── .env.example           # Пример конфигурации
├── gitleaks.toml          # Конфигурация сканера секретов
├── ruby-bot/              # Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── configmap.yaml
│       └── secret.yaml
└── .github/
    └── workflows/
        └── docker-image.yml # GitHub Actions CI/CD
```

## Безопасность

- ✅ Все секреты вынесены в переменные окружения
- ✅ Настроено сканирование секретов с gitleaks
- ✅ .env файлы исключены из Git
- ✅ Docker образы собираются через GitHub Actions
- ✅ Kubernetes секреты создаются автоматически

## Обход блокировок

### SOCKS5 Прокси

Самый простой способ - использовать SOCKS5 прокси:

```bash
TELEGRAM_PROXY_ENABLED=true
TELEGRAM_PROXY_URL=socks5://user:pass@proxy-server:port
```

### MTProxy

Для Telegram клиентов можно использовать MTProxy:

```
tg://proxy?server=t.segfault.net&port=8443&secret=bcfb182a1bafbc16ea92652628133c07
```

## Разработка

### Установка pre-commit хуков

```bash
# Установка git-secrets
brew install git-secrets
git secrets --install
git secrets --register-aws

# Установка gitleaks
brew install gitleaks
```

### Сканирование секретов

```bash
# Сканирование с gitleaks
gitleaks detect --source . --config gitleaks.toml

# Сканирование с git-secrets
git secrets --scan
```

## Поддержка

При возникновении проблем:

1. Проверьте логи: `kubectl logs -f deployment/ruby-bot -n ruby-bot`
2. Проверьте статус подов: `kubectl get pods -n ruby-bot`
3. Проверьте секреты: `kubectl get secrets -n ruby-bot`

## Лицензия

MIT License - см. файл LICENSE для деталей. 