import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Исправляем URL для использования asyncpg вместо psycopg2
if DATABASE_URL:
    # Railway дает URL в формате postgres://, но нам нужен postgresql+asyncpg://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"Инициализация базы данных с URL: {DATABASE_URL}")

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Отключаем echo для production
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Создаем фабрику сессий
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Создаем базовый класс для моделей
Base = declarative_base()
metadata = MetaData()

async def init_db():
    """Инициализация базы данных"""
    try:
        async with engine.begin() as conn:
            # Создаем все таблицы
            await conn.run_sync(Base.metadata.create_all)
        print("База данных успешно инициализирована")
    except Exception as e:
        print(f"ОШИБКА при инициализации базы данных: {e}")
        raise e

def get_async_session():
    """Возвращает фабрику асинхронных сессий"""
    return async_session
