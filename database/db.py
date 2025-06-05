import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData # Хорошо, что используете MetaData явно, хотя для Base она и так доступна

# --- Глобальные переменные для движка и фабрики сессий ---
engine = None
async_session_maker = None
Base = declarative_base() # Базовая модель для декларативного объявления таблиц
metadata = MetaData() # MetaData для работы с таблицами (если она вам нужна отдельно от Base.metadata)

# --- Инициализация базы данных ---
async def init_db():
    """
    Инициализирует подключение к базе данных, создает движок,
    фабрику сессий и, при необходимости, таблицы.
    """
    global engine, async_session_maker

    # 1. Получаем DATABASE_URL из переменных окружения
    # Это самое важное для Railway.
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        # В случае, если переменная не установлена, выбрасываем ошибку.
        # На Railway это будет означать проблему с конфигурацией.
        raise ValueError("DATABASE_URL environment variable is not set. Cannot initialize database.")

    # 2. Исправляем URL для использования asyncpg вместо psycopg2
    # Railway дает URL в формате postgres:// или postgresql://,
    # а SQLAlchemy с asyncpg требует postgresql+asyncpg://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"DEBUG: Инициализация базы данных с URL: {database_url}") # Лог для отладки

    # 3. Создаем асинхронный движок SQLAlchemy
    # echo=False для production, future=True - хорошая практика для SQLAlchemy 2.0
    # pool_pre_ping и pool_recycle помогают поддерживать соединение живым
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300, # Переподключение каждые 5 минут, чтобы избежать отваливания соединений
    )

    # 4. Создаем все таблицы, если их нет
    # Это важно делать после создания engine.
    try:
        async with engine.begin() as conn:
            # Base.metadata.create_all создаст таблицы, определенные через Base.
            # Убедитесь, что все ваши модели (User, Event и т.д.) импортированы
            # в `database/models/__init__.py` или напрямую в `db.py`
            # перед вызовом init_db, чтобы Base.metadata их "увидел".
            await conn.run_sync(Base.metadata.create_all)
        print("База данных успешно инициализирована и таблицы созданы/проверены.")
    except Exception as e:
        print(f"ОШИБКА при создании таблиц базы данных: {e}")
        # Перевыбрасываем исключение, чтобы бот не запускался без БД
        raise e

    # 5. Создаем фабрику для асинхронных сессий
    async_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False, # Обычно False, чтобы не выполнять лишние запросы
        autocommit=False, # Обычно False, чтобы явно управлять транзакциями
    )

# --- Функция для получения асинхронной сессии (для зависимостей aiogram) ---
async def get_async_session() -> AsyncSession:
    """
    Асинхронный генератор для получения сессии базы данных.
    Используется как зависимость (dependency) для обработчиков Aiogram.
    """
    if async_session_maker is None:
        raise RuntimeError("Database session maker is not initialized. Call init_db() first.")

    session = async_session_maker()
    try:
        yield session # Возвращаем сессию
    finally:
        await session.close() # Закрываем сессию после использования

# --- Важно: импортируйте ваши модели ЗДЕСЬ, чтобы Base.metadata их видел ---
# Пример:
# from database.models.user import User
# from database.models.event import Event
# from database.models.city import City
# from database.models.rating import Rating
# # ... и другие модели, которые вы определили
