import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Для отладки SQL запросов
    future=True
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
    async with engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)

def get_async_session():
    """Возвращает фабрику асинхронных сессий"""
    return async_session
