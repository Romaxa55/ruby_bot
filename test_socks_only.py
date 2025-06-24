#!/usr/bin/env python3
"""
Тест только SOCKS прокси
"""

import asyncio
import os
import time
from aiogram import Bot

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "8100762665:AAF6cJ-9WY0Ht-VUUyxhkHQkEu3hSLjhe88")

# Только SOCKS прокси
SOCKS_PROXY = "socks5://seven:bKo4uAmeZUewi45UeFRtf@91.199.87.197:2083"

async def test_socks():
    """Тестируем только SOCKS прокси"""
    try:
        print(f"🔄 Тестируем SOCKS прокси: {SOCKS_PROXY.split('@')[0]}@****")
        
        # Создаем бота с SOCKS прокси
        bot = Bot(token=BOT_TOKEN, proxy=SOCKS_PROXY)
        
        # Засекаем время
        start_time = time.time()
        
        # Тестируем подключение с увеличенным таймаутом
        print("⏳ Подключаемся к Telegram через SOCKS прокси...")
        result = await asyncio.wait_for(bot.get_me(), timeout=30.0)
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000)
        
        print(f"✅ SOCKS прокси работает!")
        print(f"📊 Время отклика: {response_time}ms")
        print(f"🤖 Бот: @{result.username}")
        
        # Закрываем сессию
        await bot.session.close()
        return True
        
    except asyncio.TimeoutError:
        print("❌ SOCKS прокси: Таймаут (30s)")
        print("💡 Возможные причины:")
        print("   - Прокси недоступен")
        print("   - Неправильные учетные данные")
        print("   - Сетевые проблемы")
        try:
            await bot.session.close()
        except:
            pass
        return False
    except Exception as e:
        print(f"❌ Ошибка SOCKS прокси: {e}")
        try:
            await bot.session.close()
        except:
            pass
        return False

async def main():
    """Основная функция"""
    print("🚀 Тестирование SOCKS прокси для Telegram Bot API")
    print("=" * 50)
    
    success = await test_socks()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SOCKS прокси работает! Можно запускать бота.")
    else:
        print("💀 SOCKS прокси НЕ работает!")
        print("\n💡 Попробуйте:")
        print("   1. Проверить интернет")
        print("   2. Обновить прокси данные") 
        print("   3. Использовать VPN")

if __name__ == "__main__":
    asyncio.run(main()) 