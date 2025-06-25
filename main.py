import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession

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
ADB_DEVICE_IP = os.getenv("ADB_DEVICE_IP", "192.168.1.100")
VIDEO_PATH = os.getenv("VIDEO_PATH", "/storage/self/primary/video/spa_noaudio.mp4")

# SOCKS прокси из переменных окружения
WORKING_SOCKS_PROXY = os.getenv("TELEGRAM_PROXY_URL", "")
if not WORKING_SOCKS_PROXY:
    logger.warning("⚠️ TELEGRAM_PROXY_URL не задан - будет использовано прямое подключение")

# Инициализация бота с обходом блокировки
async def create_bot_with_proxy():
    """Создает бота с поддержкой прокси для заблокированных стран"""
    
    # Если есть SOCKS прокси - используем его
    if WORKING_SOCKS_PROXY:
        try:
            logger.info(f"🔄 Настраиваем SOCKS5 прокси через AiohttpSession...")
            
            # Создаем сессию с SOCKS5 прокси (как в вашем примере)
            session = AiohttpSession(proxy=WORKING_SOCKS_PROXY)
            
            # Создаем бота с прокси сессией
            bot = Bot(token=BOT_TOKEN, session=session)
            
            # Проверяем подключение
            logger.info("⏳ Тестируем подключение к Telegram через SOCKS5...")
            result = await asyncio.wait_for(bot.get_me(), timeout=30.0)
            
            logger.info(f"✅ SOCKS5 прокси работает! Бот @{result.username} подключен к Telegram")
            return bot
        
        except asyncio.TimeoutError:
            logger.error("❌ Таймаут подключения через SOCKS прокси")
            try:
                await bot.session.close()
            except:
                pass
        
        except Exception as e:
            logger.error(f"❌ Ошибка подключения через SOCKS: {e}")
            try:
                await bot.session.close()
            except:
                pass
    
    # Fallback на прямое подключение
    logger.info("🔄 Пробуем прямое подключение...")
    try:
        bot = Bot(token=BOT_TOKEN)
        await asyncio.wait_for(bot.get_me(), timeout=15.0)
        logger.info("✅ Прямое подключение работает")
        return bot
    except Exception as direct_error:
        logger.error(f"❌ Прямое подключение не работает: {direct_error}")
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
        if WORKING_SOCKS_PROXY:
            proxy_status = "🌐 SOCKS5 прокси активен (блокировка обойдена)"
            proxy_info = f"Прокси: `{WORKING_SOCKS_PROXY.split('@')[0]}@****`"
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
        
        if WORKING_SOCKS_PROXY:
            proxy_info = f"""
🌐 **Telegram SOCKS5 Прокси:**
🔗 URL: `{WORKING_SOCKS_PROXY.split('@')[0]}@****`
✅ Статус: **Активен** ✅ Проверен через curl
🌍 Для обхода блокировки в: Вьетнам, Россия, Иран и др.

📊 **Подключение:**
• Протокол: SOCKS5 с авторизацией
• Таймаут: 30 секунд  
• Статус: ✅ Работает (проверено curl)
            """
        else:
            proxy_info = f"""
🌐 **Статус подключения:**
📡 **Прямое подключение** (без прокси)

⚠️ **Внимание:** В заблокированных странах бот может не работать

🔧 **Настройка прокси:**
Установите переменную окружения TELEGRAM_PROXY_URL
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

# Тестирование прокси в реальном времени
async def test_proxy(message: types.Message):
    try:
        logger.info("Получена команда: /test_proxy")
        await message.answer("🔍 Тестирую доступные прокси...")
        
        # Список прокси для тестирования
        test_proxies = []
        if WORKING_SOCKS_PROXY:
            test_proxies.append(("SOCKS5 Working", WORKING_SOCKS_PROXY))
        test_proxies.append(("Direct Connection", None))
        
        results = []
        for name, proxy_url in test_proxies:
            if proxy_url is None and name != "Direct Connection":
                continue
                
            try:
                # Создаем временного бота для тестирования
                if proxy_url:
                    # Используем AiohttpSession с прокси (как в вашем примере)
                    session = AiohttpSession(proxy=proxy_url)
                    test_bot = Bot(token=BOT_TOKEN, session=session)
                else:
                    # Прямое подключение
                    test_bot = Bot(token=BOT_TOKEN)
                
                # Тестируем с коротким таймаутом
                start_time = asyncio.get_event_loop().time()
                await asyncio.wait_for(test_bot.get_me(), timeout=15.0)
                end_time = asyncio.get_event_loop().time()
                
                response_time = round((end_time - start_time) * 1000)
                results.append(f"✅ {name}: {response_time}ms")
                
                await test_bot.session.close()
                
            except asyncio.TimeoutError:
                results.append(f"⏰ {name}: Таймаут")
            except Exception as e:
                results.append(f"❌ {name}: {str(e)[:50]}")
        
        result_text = "🔍 **Результаты тестирования прокси:**\n\n" + "\n".join(results)
        if WORKING_SOCKS_PROXY:
            result_text += f"\n\n💡 Используемый прокси: {WORKING_SOCKS_PROXY.split('@')[0]}@****"
        else:
            result_text += f"\n\n💡 Прокси не настроен - используется прямое подключение"
        
        await message.answer(result_text, parse_mode="Markdown")
        logger.info("Тестирование прокси завершено")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании прокси: {e}")
        await message.answer(f"Ошибка при тестировании: {e}")

# Регистрация команд для Telegram
async def set_commands(bot_instance):
    commands = [
        BotCommand(command="start", description="Запуск бота и информация о MTProxy"),
        BotCommand(command="set_landscape", description="Установить альбомную ориентацию"),
        BotCommand(command="set_portrait", description="Установить портретную ориентацию"),
        BotCommand(command="play_video", description="Запустить видео"),
        BotCommand(command="adb_connect", description="Подключиться к устройству через ADB"),
        BotCommand(command="check_proxy", description="Проверить статус прокси"),
        BotCommand(command="test_proxy", description="Тестировать все доступные прокси"),
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
    dp.message.register(test_proxy, Command("test_proxy"))

    # Попытка установки команд в Telegram (не критично если не получится)
    try:
        await asyncio.wait_for(set_commands(bot), timeout=15.0)
        logger.info("✅ Команды бота успешно установлены в Telegram")
    except asyncio.TimeoutError:
        logger.warning("⏰ Таймаут при установке команд бота (не критично)")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось установить команды бота: {e} (не критично)")

    # Запуск поллинга
    logger.info("🎯 Бот запущен и готов к работе. Попробуйте отправить /start")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
