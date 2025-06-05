import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

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
            # Благодаря импорту `models` ниже, Base.metadata "увидит" все ваши модели.
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

# --- ИСПРАВЛЕННАЯ функция для получения асинхронной сессии ---
def get_async_session():
    """
    Функция для получения новой сессии базы данных.
    Возвращает объект AsyncSession, который нужно закрывать после использования.
    
    Использование:
    session = get_async_session()
    try:
        # работа с сессией
        result = await session.execute(query)
        await session.commit()
    finally:
        await session.close()
    """
    if async_session_maker is None:
        raise RuntimeError("Database session maker is not initialized. Call init_db() first.")
    
    return async_session_maker()

# --- Контекстный менеджер для сессии (альтернативный способ) ---
class AsyncSessionContext:
    """
    Асинхронный контекстный менеджер для сессии базы данных.
    
    Использование:
    async with AsyncSessionContext() as session:
        result = await session.execute(query)
        await session.commit()
    """
    
    def __init__(self):
        if async_session_maker is None:
            raise RuntimeError("Database session maker is not initialized. Call init_db() first.")
        self.session = None
    
    async def __aenter__(self):
        self.session = async_session_maker()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                await self.session.rollback()
            await self.session.close()

# --- Вспомогательная функция для безопасной работы с сессией ---
async def safe_session_execute(operation):
    """
    Безопасное выполнение операции с базой данных.
    
    Args:
        operation: async функция, которая принимает session и выполняет операции с БД
    
    Returns:
        Результат операции или None в случае ошибки
    
    Example:
        async def my_operation(session):
            result = await session.execute(select(User).where(User.id == 1))
            return result.scalar_one_or_none()
        
        user = await safe_session_execute(my_operation)
    """
    session = None
    try:
        session = get_async_session()
        result = await operation(session)
        await session.commit()
        return result
    except Exception as e:
        if session:
            await session.rollback()
        print(f"Ошибка при выполнении операции с БД: {e}")
        raise e
    finally:
        if session:
            await session.close()

# --- ОБЯЗАТЕЛЬНО: Импортируем ваш файл models.py, где определены все модели ---
# Это позволяет SQLAlchemy обнаружить все модели, наследующие от Base,
# и создать для них таблицы при вызове Base.metadata.create_all().
try:
    from database import models # Импортируем models.py, который находится в той же папке database
    print("Модели базы данных успешно импортированы")
except ImportError as e:
    print(f"ПРЕДУПРЕЖДЕНИЕ: Не удалось импортировать модели: {e}")
