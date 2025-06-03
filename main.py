import os
print("DEBUG: Все переменные окружения:")
for key, value in os.environ.items():
    print(f"{key}: {value[:5]}..." if value and len(value) > 10 else f"{key}: {value}")

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from database.db import init_db, get_async_session
from handlers import common, profile, events, ratings, menu_fixed as menu, registration
from middlewares.auth import AuthMiddleware

# Добавьте эти строки для отладки
print("DEBUG: BOT_TOKEN from config:", BOT_TOKEN)
print("DEBUG: BOT_TOKEN from environment:", os.environ.get("BOT_TOKEN"))

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Изменили на DEBUG для более подробных логов
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Команды бота
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="help", description="Получить справку"),
        BotCommand(command="profile", description="Мой профиль"),
        BotCommand(command="events", description="Мероприятия"),
        BotCommand(command="create", description="Создать мероприятие"),
        BotCommand(command="knowledge", description="База знаний"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Проверка токена перед инициализацией бота
    if not BOT_TOKEN:
        print("ОШИБКА: BOT_TOKEN не определен!")
        return
        
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Инициализация базы данных
    try:
        await init_db()
        print("База данных успешно инициализирована")
    except Exception as e:
        print(f"ОШИБКА при инициализации базы данных: {e}")
        return
    
    # Регистрация обработчиков
    print("Регистрация обработчиков...")
dp.include_router(menu.router)
dp.include_router(registration.router)  # Добавляем роутер регистрации
dp.include_router(common.router)
dp.include_router(profile.router)
dp.include_router(events.router)
dp.include_router(ratings.router)
    print("Обработчики зарегистрированы успешно")
    
    # Регистрация middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Установка команд бота
    await set_commands(bot)
    
    # Удаление вебхука (на случай, если бот ранее использовал вебхук)
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Бот успешно запущен и начинает опрос обновлений")
    
    # Запуск опроса обновлений
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
