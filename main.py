import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from database.db import init_db
from handlers import common, profile, events, ratings, menu_fixed as menu, registration

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Команды бота
async def set_commands(bot: Bot):
    """Устанавливает команды бота в меню Telegram"""
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="help", description="Получить справку"),
        BotCommand(command="profile", description="Мой профиль"),
        BotCommand(command="events", description="Мероприятия"),
        BotCommand(command="create", description="Создать мероприятие"),
        BotCommand(command="knowledge", description="База знаний"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Команды бота установлены")

async def main():
    """Основная функция запуска бота"""
    
    # 1. Проверка токена
    if not BOT_TOKEN:
        logger.error("КРИТИЧЕСКАЯ ОШИБКА: BOT_TOKEN не определен!")
        logger.error("Проверьте переменные окружения в Railway")
        return
    
    logger.info("BOT_TOKEN найден, начинаем инициализацию...")
    
    # 2. Инициализация базы данных
    try:
        logger.info("Инициализация базы данных...")
        await init_db()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА при инициализации базы данных: {e}")
        return
    
    # 3. Создание бота и диспетчера
    logger.info("Создание экземпляра бота...")
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # 4. Регистрация обработчиков (ПОРЯДОК ВАЖЕН!)
    logger.info("Регистрация обработчиков...")
    
    # Сначала регистрация (самые специфичные обработчики)
    dp.include_router(registration.router)
    logger.info("✓ Обработчики регистрации зарегистрированы")
    
    # Затем меню (содержит основную логику)
    dp.include_router(menu.router)
    logger.info("✓ Обработчики меню зарегистрированы")
    
    # Остальные обработчики
    dp.include_router(common.router)
    dp.include_router(profile.router)
    dp.include_router(events.router)
    dp.include_router(ratings.router)
    logger.info("✓ Все обработчики зарегистрированы")
    
    # 5. Установка команд бота
    try:
        await set_commands(bot)
    except Exception as e:
        logger.warning(f"Не удалось установить команды бота: {e}")
    
    # 6. КРИТИЧЕСКАЯ ОЧИСТКА для решения конфликта
    logger.info("Очистка webhook и pending updates...")
    try:
        # Принудительное удаление webhook
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✓ Webhook удален")
        
        # Небольшая пауза для гарантированной очистки
        await asyncio.sleep(1)
        
        # Дополнительная очистка pending updates
        try:
            updates = await bot.get_updates(timeout=1, limit=100)
            if updates:
                logger.info(f"Очищено {len(updates)} накопившихся обновлений")
        except Exception:
            pass  # Игнорируем ошибки при очистке
            
    except Exception as e:
        logger.warning(f"Ошибка при очистке webhook: {e}")
    
    # 7. Запуск polling с обработкой ошибок
    logger.info("🚀 Запуск бота в режиме long polling...")
    
    try:
        # Указываем конкретные типы обновлений для обработки
        allowed_updates = [
            "message", 
            "callback_query", 
            "inline_query", 
            "chosen_inline_result"
        ]
        
        await dp.start_polling(
            bot, 
            allowed_updates=allowed_updates,
            skip_updates=True,  # Пропускаем старые обновления
            handle_signals=False  # Отключаем обработку сигналов для Railway
        )
        
    except Exception as e:
        logger.error(f"Ошибка при запуске polling: {e}")
    finally:
        # Гарантированное закрытие сессии бота
        await bot.session.close()
        logger.info("Сессия бота закрыта")

if __name__ == "__main__":
    try:
        # Запуск с обработкой исключений
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")
