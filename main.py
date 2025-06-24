import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector
import aiohttp

# Настройка логирования для вывода в stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Вывод только в stdout
)

# Логгер
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения (для кубернетеса)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Настройки MTProxy для обхода блокировки во Вьетнаме
MTPROXY_HOST = os.getenv("MTPROXY_HOST", "t.segfault.net")
MTPROXY_PORT = int(os.getenv("MTPROXY_PORT", "8443"))
MTPROXY_SECRET = os.getenv("MTPROXY_SECRET", "PLACEHOLDER_SECRET")

# ADB настройки
ADB_DEVICE_IP = os.getenv("ADB_DEVICE_IP", "10.0.0.159")
VIDEO_PATH = os.getenv("VIDEO_PATH", "/storage/self/primary/video/spa_noaudio.mp4")

# Функция создания сессии с прокси
def create_proxy_session():
    try:
        # Используем SOCKS5 прокси если указан в переменных окружения
        socks_proxy = os.getenv("SOCKS_PROXY")
        if socks_proxy:
            logger.info(f"Используем SOCKS прокси: {socks_proxy}")
            connector = ProxyConnector.from_url(socks_proxy)
            session = AiohttpSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30)
            )
            return session
        
        # Если SOCKS прокси не указан, используем прямое подключение
        # MTProxy нужно настраивать на уровне системы или через отдельный клиент
        logger.info("SOCKS прокси не указан, используем прямое подключение")
        logger.info(f"MTProxy доступен: tg://proxy?server={MTPROXY_HOST}&port={MTPROXY_PORT}&secret={MTPROXY_SECRET}")
        return None
        
    except Exception as e:
        logger.error(f"Ошибка создания прокси сессии: {e}")
        logger.info("Использую стандартную сессию без прокси")
        return None

# Инициализация бота с поддержкой прокси
try:
    proxy_session = create_proxy_session()
    if proxy_session:
        bot = Bot(token=BOT_TOKEN, session=proxy_session)
        logger.info("Бот запущен с SOCKS прокси")
    else:
        bot = Bot(token=BOT_TOKEN)
        logger.info("Бот запущен с прямым подключением")
        logger.info("Для обхода блокировки настройте MTProxy в Telegram клиенте")
except Exception as e:
    logger.error(f"Ошибка инициализации бота с прокси: {e}")
    bot = Bot(token=BOT_TOKEN)
    logger.info("Бот запущен без прокси (fallback)")

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
        
        socks_proxy = os.getenv("SOCKS_PROXY")
        proxy_status = "✅ SOCKS прокси активен" if socks_proxy else "📡 Прямое подключение"
        
        welcome_text = f"""
🤖 **Добро пожаловать в Ruby Bot!**

🌐 **Статус подключения:** {proxy_status}

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
        await message.answer("Проверяю статус прокси...")
        
        socks_proxy = os.getenv("SOCKS_PROXY")
        if socks_proxy:
            proxy_info = f"""
🌐 **Статус SOCKS прокси:**
🔗 Прокси: `{socks_proxy}`
✅ Бот использует SOCKS прокси для подключения

📱 **MTProxy для Telegram клиента:**
📡 Сервер: `{MTPROXY_HOST}`
🔌 Порт: `{MTPROXY_PORT}`
🔗 Ссылка: `tg://proxy?server={MTPROXY_HOST}&port={MTPROXY_PORT}&secret={MTPROXY_SECRET}`
            """
        else:
            proxy_info = f"""
🌐 **Статус подключения:**
📡 Прямое подключение (без SOCKS прокси)

📱 **MTProxy для Telegram клиента:**
📡 Сервер: `{MTPROXY_HOST}`
🔌 Порт: `{MTPROXY_PORT}`
🔗 Ссылка: `tg://proxy?server={MTPROXY_HOST}&port={MTPROXY_PORT}&secret={MTPROXY_SECRET}`

💡 Для бота установите переменную `SOCKS_PROXY` если нужен прокси
            """
        
        await message.answer(proxy_info, parse_mode="Markdown")
        logger.info("Информация о прокси отправлена")
        
    except Exception as e:
        logger.error(f"Ошибка при проверке прокси: {e}")
        await message.answer(f"Ошибка: {e}")

# Регистрация команд для Telegram
async def set_commands():
    commands = [
        BotCommand(command="start", description="Запуск бота и информация о MTProxy"),
        BotCommand(command="set_landscape", description="Установить альбомную ориентацию"),
        BotCommand(command="set_portrait", description="Установить портретную ориентацию"),
        BotCommand(command="play_video", description="Запустить видео"),
        BotCommand(command="adb_connect", description="Подключиться к устройству через ADB"),
        BotCommand(command="check_proxy", description="Проверить статус прокси"),
    ]
    await bot.set_my_commands(commands)

# Настройка маршрутов
async def main():
    # Регистрация хэндлеров
    dp.message.register(start_command, Command("start"))
    dp.message.register(set_landscape, Command("set_landscape"))
    dp.message.register(set_portrait, Command("set_portrait"))
    dp.message.register(play_video, Command("play_video"))
    dp.message.register(adb_connect, Command("adb_connect"))
    dp.message.register(check_proxy, Command("check_proxy"))

    # Установка команд в Telegram
    await set_commands()

    # Запуск поллинга
    logger.info("Бот запущен и готов к работе.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
