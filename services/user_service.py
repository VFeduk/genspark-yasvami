from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User, Gender, UserType

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User:
    """
    Получает пользователя по его Telegram ID.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        telegram_id: ID пользователя в Telegram
    
    Returns:
        Объект пользователя или None, если пользователь не найден
    """
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()

async def create_user(session: AsyncSession, telegram_id: int, username: str, first_name: str,
                     last_name: str, city: str, display_name: str, age: int, gender: Gender,
                     about: str = None) -> User:
    """
    Создает нового пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        telegram_id: ID пользователя в Telegram
        username: Username пользователя в Telegram
        first_name: Имя пользователя в Telegram
        last_name: Фамилия пользователя в Telegram
        city: Город пользователя
        display_name: Отображаемое имя пользователя
        age: Возраст пользователя
        gender: Пол пользователя (MALE/FEMALE)
        about: Информация о пользователе
    
    Returns:
        Созданный объект пользователя
    """
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        city=city,
        display_name=display_name,
        age=age,
        gender=gender,
        about=about,
        rating=100,  # Начальный рейтинг
        tokens=0,
        user_type=UserType.REGULAR
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

async def update_user(session: AsyncSession, user: User, **kwargs) -> User:
    """
    Обновляет данные пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user: Объект пользователя
        **kwargs: Поля для обновления
    
    Returns:
        Обновленный объект пользователя
    """
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    await session.commit()
    await session.refresh(user)
    
    return user

async def add_tokens(session: AsyncSession, user: User, amount: int) -> User:
    """
    Добавляет токены пользователю.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user: Объект пользователя
        amount: Количество токенов для добавления
    
    Returns:
        Обновленный объект пользователя
    """
    user.tokens += amount
    await session.commit()
    await session.refresh(user)
    
    return user