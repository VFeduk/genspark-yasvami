from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from config import DATABASE_URL
from database.models import Base

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(DATABASE_URL, poolclass=NullPool, echo=False)

# Создание фабрики сессий
async_session_factory = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        # Создаем таблицы, если они еще не существуют
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session():
    """Асинхронный контекстный менеджер для сессии БД"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()