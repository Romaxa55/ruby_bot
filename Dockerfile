FROM python:3.11-alpine

# Установим необходимые зависимости для ADB и Python
RUN apk add --no-cache bash openjdk11 android-tools

# Установка рабочей директории
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем локальный сервер ADB, чтобы он автоматически запускался
CMD ["python", "bot.py"]
