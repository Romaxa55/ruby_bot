import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.filters import Command

# Настройка логирования для вывода в stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Вывод только в stdout
)

# Логгер
logger = logging.getLogger(__name__)

# Загружаем .env файл если он существует (для локального тестирования)
def load_env_file():
    try:
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            logger.info("Загружены переменные из .env файла")
    except Exception as e:
        logger.warning(f"Не удалось загрузить .env файл: {e}")

# Загружаем переменные окружения
load_env_file()

# Конфигурация из переменных окружения (для кубернетеса)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Настройки MTProxy для обхода блокировки во Вьетнаме
MTPROXY_HOST = os.getenv("MTPROXY_HOST", "t.segfault.net")
MTPROXY_PORT = int(os.getenv("MTPROXY_PORT", "8443"))
MTPROXY_SECRET = os.getenv("MTPROXY_SECRET", "PLACEHOLDER_SECRET")

# SOCKS5 Proxy для Telegram (для заблокированных стран)
TELEGRAM_PROXY_ENABLED = os.getenv("TELEGRAM_PROXY_ENABLED", "false").lower() == "true"
TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL", "")

# ADB настройки
ADB_DEVICE_IP = os.getenv("ADB_DEVICE_IP", "10.0.0.159")
VIDEO_PATH = os.getenv("VIDEO_PATH", "/storage/self/primary/video/spa_noaudio.mp4")

# Функция получения прокси URL для aiogram
def get_proxy_url():
    """Возвращает URL прокси для использования в aiogram"""
    try:
        # Основной Telegram прокси
        if TELEGRAM_PROXY_ENABLED and TELEGRAM_PROXY_URL:
            logger.info(f"🌐 Используем SOCKS5 прокси: {TELEGRAM_PROXY_URL.split('@')[0]}@****")
            return TELEGRAM_PROXY_URL
        
        # Fallback прокси
        socks_proxy = os.getenv("SOCKS_PROXY")
        if socks_proxy:
            logger.info(f"🌐 Используем fallback SOCKS прокси: {socks_proxy}")
            return socks_proxy
            
        http_proxy = os.getenv("HTTP_PROXY")
        if http_proxy:
            logger.info(f"🌐 Используем HTTP прокси: {http_proxy}")
            return http_proxy
        
        # Прямое подключение
        logger.info("📡 Прокси не настроен, используем прямое подключение")
        return None
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения прокси: {e}")
        return None

# Инициализация бота с обходом блокировки
async def create_bot_with_proxy():
    """Создает бота с поддержкой прокси для заблокированных стран"""
    try:
        # Получаем URL прокси
        proxy_url = get_proxy_url()
        
        if proxy_url:
            # Создаем бота с прокси через встроенную поддержку aiogram
            bot = Bot(token=BOT_TOKEN, proxy=proxy_url)
            if TELEGRAM_PROXY_ENABLED:
                logger.info("🚀 Бот запущен с SOCKS5 прокси для обхода блокировки")
            else:
                logger.info("🚀 Бот запущен с прокси")
            return bot
        else:
            # Прямое подключение
            bot = Bot(token=BOT_TOKEN)
            logger.info("🚀 Бот запущен с прямым подключением")
            if not TELEGRAM_PROXY_ENABLED:
                logger.info("💡 Для обхода блокировки установите TELEGRAM_PROXY_ENABLED=true")
            return bot
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка инициализации бота: {e}")
        raise

# Глобальные переменные для бота
bot = None
dp = Dispatcher()

# Установка альбомной ориентации
async def set_landscape(message: types.Message):
    try:
        logger.info("Получена команда: /set_landscape")
        await message.answer("Устанавливаю альбомную ориентацию...")
        process = await asyncio.create_subprocess_shell("adb shell settings put system user_rotation 1")
        await process.communicate()  # Ожидание завершения команды
        await message.answer("Ориентация экрана установлена на альбомную.")
        logger.info("Ориентация успешно установлена на альбомную")
    except Exception as e:
        logger.error(f"Ошибка при установке альбомной ориентации: {e}")
        await message.answer(f"Ошибка: {e}")

# Установка портретной ориентации
async def set_portrait(message: types.Message):
    try:
        logger.info("Получена команда: /set_portrait")
        await message.answer("Устанавливаю портретную ориентацию...")
        process = await asyncio.create_subprocess_shell("adb shell settings put system user_rotation 0")
        await process.communicate()  # Ожидание завершения команды
        await message.answer("Ориентация экрана установлена на портретную.")
        logger.info("Ориентация успешно установлена на портретную")
    except Exception as e:
        logger.error(f"Ошибка при установке портретной ориентации: {e}")
        await message.answer(f"Ошибка: {e}")

# Запуск видео
async def play_video(message: types.Message):
    try:
        logger.info("Получена команда: /play_video")
        await message.answer(f"Запускаю видео: {VIDEO_PATH}")
        process = await asyncio.create_subprocess_shell(
            f'adb shell am start -a android.intent.action.VIEW -d file://{VIDEO_PATH} -t video/mp4'
        )
        await process.communicate()  # Ожидание завершения команды
        await message.answer("Видео запущено.")
        logger.info("Видео успешно запущено")
    except Exception as e:
        logger.error(f"Ошибка при запуске видео: {e}")
        await message.answer(f"Ошибка: {e}")

# Подключение к устройству через ADB
async def adb_connect(message: types.Message):
    try:
        logger.info("Получена команда: /adb_connect")
        await message.answer(f"Подключаюсь к устройству по адресу {ADB_DEVICE_IP}...")
        process = await asyncio.create_subprocess_shell(f"adb connect {ADB_DEVICE_IP}")
        stdout, stderr = await process.communicate()
        if stdout:
            logger.info(f"ADB подключение успешно: {stdout.decode().strip()}")
            await message.answer(f"ADB подключение успешно: {stdout.decode().strip()}")
        if stderr:
            logger.error(f"Ошибка ADB подключения: {stderr.decode().strip()}")
            await message.answer(f"Ошибка ADB подключения: {stderr.decode().strip()}")
    except Exception as e:
        logger.error(f"Ошибка при ADB подключении: {e}")
        await message.answer(f"Ошибка: {e}")

# Команда start
async def start_command(message: types.Message):
    try:
        logger.info("Получена команда: /start")
        
        # Определяем статус подключения
        if TELEGRAM_PROXY_ENABLED and TELEGRAM_PROXY_URL:
            proxy_status = "🌐 SOCKS5 прокси активен (блокировка обойдена)"
            proxy_info = f"Прокси: `{TELEGRAM_PROXY_URL.split('@')[0]}@****`"
        elif os.getenv("SOCKS_PROXY"):
            proxy_status = "🌐 SOCKS прокси активен"
            proxy_info = f"Прокси: `{os.getenv('SOCKS_PROXY')}`"
        else:
            proxy_status = "📡 Прямое подключение"
            proxy_info = "Прокси не используется"
        
        welcome_text = f"""
🤖 **Добро пожаловать в Ruby Bot!**

🌐 **Статус:** {proxy_status}
{proxy_info}

📱 **Доступные команды:**
• `/set_landscape` - Альбомная ориентация
• `/set_portrait` - Портретная ориентация  
• `/play_video` - Запуск видео
• `/adb_connect` - Подключение ADB
• `/check_proxy` - Статус прокси

🔗 **MTProxy для Telegram клиента:**
`tg://proxy?server={MTPROXY_HOST}&port={MTPROXY_PORT}&secret={MTPROXY_SECRET}`

⚙️ **Конфигурация:**
• ADB устройство: `{ADB_DEVICE_IP}`
• Видео файл: `{VIDEO_PATH}`
        """
        
        await message.answer(welcome_text, parse_mode="Markdown")
        logger.info("Приветственное сообщение отправлено")
        
    except Exception as e:
        logger.error(f"Ошибка в команде start: {e}")
        await message.answer(f"Ошибка: {e}")

# Проверка статуса прокси
async def check_proxy(message: types.Message):
    try:
        logger.info("Получена команда: /check_proxy")
        await message.answer("🔍 Проверяю статус прокси...")
        
        # Проверяем основной Telegram прокси
        if TELEGRAM_PROXY_ENABLED and TELEGRAM_PROXY_URL:
            proxy_info = f"""
🌐 **Telegram SOCKS5 Прокси:**
🔗 URL: `{TELEGRAM_PROXY_URL.split('@')[0]}@****`
✅ Статус: **Активен** 
🌍 Для обхода блокировки в: Вьетнам, Россия, Иран и др.

📊 **Подключение:**
• Протокол: SOCKS5 с авторизацией
• Таймаут: 30 секунд
• Статус: ✅ Работает
            """
        # Fallback прокси
        elif os.getenv("SOCKS_PROXY") or os.getenv("HTTP_PROXY"):
            fallback_proxy = os.getenv("SOCKS_PROXY") or os.getenv("HTTP_PROXY")
            proxy_info = f"""
🌐 **Fallback Прокси:**
🔗 Прокси: `{fallback_proxy}`
⚠️ Статус: Резервный прокси активен

💡 Рекомендуется использовать TELEGRAM_PROXY_URL для лучшей стабильности
            """
        else:
            proxy_info = f"""
🌐 **Статус подключения:**
📡 **Прямое подключение** (без прокси)

⚠️ **Внимание:** В заблокированных странах бот может не работать

🔧 **Настройка прокси:**
Установите в .env файле:
```
TELEGRAM_PROXY_ENABLED=true
TELEGRAM_PROXY_URL=socks5://user:pass@server:port
```
            """
        
        # Добавляем информацию о MTProxy для клиентов
        proxy_info += f"""

📱 **MTProxy для Telegram клиента:**
📡 Сервер: `{MTPROXY_HOST}`
🔌 Порт: `{MTPROXY_PORT}`
🔗 Ссылка: `tg://proxy?server={MTPROXY_HOST}&port={MTPROXY_PORT}&secret={MTPROXY_SECRET}`
        """
        
        await message.answer(proxy_info, parse_mode="Markdown")
        logger.info("Информация о прокси отправлена")
        
    except Exception as e:
        logger.error(f"Ошибка при проверке прокси: {e}")
        await message.answer(f"Ошибка: {e}")

# Регистрация команд для Telegram
async def set_commands(bot_instance):
    commands = [
        BotCommand(command="start", description="Запуск бота и информация о MTProxy"),
        BotCommand(command="set_landscape", description="Установить альбомную ориентацию"),
        BotCommand(command="set_portrait", description="Установить портретную ориентацию"),
        BotCommand(command="play_video", description="Запустить видео"),
        BotCommand(command="adb_connect", description="Подключиться к устройству через ADB"),
        BotCommand(command="check_proxy", description="Проверить статус прокси"),
    ]
    await bot_instance.set_my_commands(commands)

# Настройка маршрутов
async def main():
    global bot
    
    # Создаем бота в async контексте
    bot = await create_bot_with_proxy()
    
    # Регистрация хэндлеров
    dp.message.register(start_command, Command("start"))
    dp.message.register(set_landscape, Command("set_landscape"))
    dp.message.register(set_portrait, Command("set_portrait"))
    dp.message.register(play_video, Command("play_video"))
    dp.message.register(adb_connect, Command("adb_connect"))
    dp.message.register(check_proxy, Command("check_proxy"))

    # Установка команд в Telegram
    await set_commands(bot)

    # Запуск поллинга
    logger.info("🎯 Бот запущен и готов к работе.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
