import logging
import asyncio
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

# Токен вашего бота
BOT_TOKEN = "8100762665:AAF6cJ-9WY0Ht-VUUyxhkHQkEu3hSLjhe88"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
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
        video_path = "/storage/self/primary/video/spa_noaudio.mp4"
        await message.answer(f"Запускаю видео: {video_path}")
        process = await asyncio.create_subprocess_shell(
            f'adb shell am start -a android.intent.action.VIEW -d file://{video_path} -t video/mp4'
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
        # Укажите IP-адрес устройства
        device_ip = "10.0.0.159"
        await message.answer(f"Подключаюсь к устройству по адресу {device_ip}...")
        process = await asyncio.create_subprocess_shell(f"adb connect {device_ip}")
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

# Регистрация команд для Telegram
async def set_commands():
    commands = [
        BotCommand(command="set_landscape", description="Установить альбомную ориентацию"),
        BotCommand(command="set_portrait", description="Установить портретную ориентацию"),
        BotCommand(command="play_video", description="Запустить видео"),
        BotCommand(command="adb_connect", description="Подключиться к устройству через ADB"),
    ]
    await bot.set_my_commands(commands)

# Настройка маршрутов
async def main():
    # Регистрация хэндлеров
    dp.message.register(set_landscape, Command("set_landscape"))
    dp.message.register(set_portrait, Command("set_portrait"))
    dp.message.register(play_video, Command("play_video"))
    dp.message.register(adb_connect, Command("adb_connect"))

    # Установка команд в Telegram
    await set_commands()

    # Запуск поллинга
    logger.info("Бот запущен и готов к работе.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
