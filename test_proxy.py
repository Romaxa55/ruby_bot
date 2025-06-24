#!/usr/bin/env python3
"""
Скрипт для тестирования различных прокси с Telegram Bot API
"""

import asyncio
import os
import time
from aiogram import Bot

# Загружаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "8100762665:AAF6cJ-9WY0Ht-VUUyxhkHQkEu3hSLjhe88")

# Список прокси для тестирования
TEST_PROXIES = [
    ("Direct Connection", None),
    ("HTTP Vietnam 1", "http://103.148.72.192:80"),
    ("HTTP Vietnam 2", "http://103.149.162.194:80"), 
    ("HTTP Vietnam 3", "http://103.155.196.25:8080"),
    ("SOCKS5 Premium", "socks5://seven:bKo4uAmeZUewi45UeFRtf@91.199.87.197:2083"),
    ("SOCKS5 Free 1", "socks5://203.95.198.39:1080"),
    ("SOCKS5 Free 2", "socks5://5.189.179.173:7497"),
]

async def test_proxy(name, proxy_url, timeout=10):
    """Тестирует один прокси"""
    try:
        print(f"🔄 Тестируем {name}...")
        
        # Создаем бота
        bot = Bot(token=BOT_TOKEN, proxy=proxy_url) if proxy_url else Bot(token=BOT_TOKEN)
        
        # Засекаем время
        start_time = time.time()
        
        # Тестируем подключение
        result = await asyncio.wait_for(bot.get_me(), timeout=timeout)
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000)
        
        # Закрываем сессию
        await bot.session.close()
        
        print(f"✅ {name}: {response_time}ms - OK")
        return True, response_time
        
    except asyncio.TimeoutError:
        print(f"⏰ {name}: Таймаут ({timeout}s)")
        try:
            await bot.session.close()
        except:
            pass
        return False, None
    except Exception as e:
        print(f"❌ {name}: {str(e)[:100]}")
        try:
            await bot.session.close()
        except:
            pass
        return False, None

async def main():
    """Основная функция тестирования"""
    print("🚀 Начинаю тестирование прокси для Telegram Bot API")
    print("=" * 60)
    
    working_proxies = []
    
    for name, proxy_url in TEST_PROXIES:
        success, response_time = await test_proxy(name, proxy_url)
        
        if success:
            working_proxies.append((name, proxy_url, response_time))
        
        # Небольшая пауза между тестами
        await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    if working_proxies:
        # Сортируем по времени отклика
        working_proxies.sort(key=lambda x: x[2])
        
        print("✅ Рабочие прокси (отсортированы по скорости):")
        for name, proxy_url, response_time in working_proxies:
            print(f"   • {name}: {response_time}ms")
            if proxy_url:
                print(f"     URL: {proxy_url}")
        
        print(f"\n🏆 Лучший прокси: {working_proxies[0][0]} ({working_proxies[0][2]}ms)")
        
        if working_proxies[0][1]:  # Если не прямое подключение
            print(f"💡 Добавьте в .env:")
            if "socks5://" in working_proxies[0][1]:
                print(f"TELEGRAM_PROXY_ENABLED=true")
                print(f"TELEGRAM_PROXY_URL={working_proxies[0][1]}")
            else:
                print(f"HTTP_PROXY_1={working_proxies[0][1]}")
                print(f"TELEGRAM_PROXY_ENABLED=false")
    else:
        print("❌ Ни один прокси не работает!")
        print("💡 Попробуйте:")
        print("   1. Проверить интернет соединение")
        print("   2. Использовать VPN")
        print("   3. Найти актуальные прокси в интернете")

if __name__ == "__main__":
    asyncio.run(main()) 