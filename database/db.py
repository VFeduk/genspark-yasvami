from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from config import DATABASE_URL

# Создание асинхронного движка SQLAlchemy
# Убедимся, что URL начинается с postgresql+asyncpg://
db_url = DATABASE_URL
if not db_url.startswith("postgresql+asyncpg://"):
    # Заменяем postgresql:// на postgresql+asyncpg://
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(db_url, poolclass=NullPool, echo=False)

# Создание фабрики сессий
async_session_factory = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    """Инициализация базы данных"""
    print(f"Инициализация базы данных с URL: {db_url}")
    try:
        async with engine.begin() as conn:
            # Создаем таблицы, если они еще не существуют
            from database.models import Base
            await conn.run_sync(Base.metadata.create_all)
        print("База данных успешно инициализирована")
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        raise

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
