from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, not_

from database.models import User, Event, Rating, event_participants

async def rate_user(session: AsyncSession, event_id: int, rater_id: int, rated_id: int, score: int) -> Rating:
    """
    Создает оценку пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        event_id: ID мероприятия
        rater_id: ID пользователя, который оценивает
        rated_id: ID пользователя, которого оценивают
        score: Оценка (от 1 до 5)
    
    Returns:
        Созданный объект оценки
    """
    # Проверяем, существует ли уже оценка
    result = await session.execute(
        select(Rating).where(
            and_(
                Rating.event_id == event_id,
                Rating.rater_id == rater_id,
                Rating.rated_id == rated_id
            )
        )
    )
    existing_rating = result.scalars().first()
    
    if existing_rating:
        # Если оценка уже существует, обновляем её
        existing_rating.score = score
        await session.commit()
        await session.refresh(existing_rating)
        return existing_rating
    
    # Иначе создаем новую оценку
    rating = Rating(
        event_id=event_id,
        rater_id=rater_id,
        rated_id=rated_id,
        score=score
    )
    
    session.add(rating)
    await session.commit()
    await session.refresh(rating)
    
    return rating

async def update_user_rating(session: AsyncSession, user_id: int, rating_change: int) -> User:
    """
    Обновляет рейтинг пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        rating_change: Изменение рейтинга (положительное или отрицательное число)
    
    Returns:
        Обновленный объект пользователя
    """
    # Получаем пользователя
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return None
    
    # Обновляем рейтинг
    user.rating += rating_change
    
    # Проверяем, не ушел ли рейтинг в отрицательные значения
    if user.rating < 0:
        user.rating = 0
    
    await session.commit()
    await session.refresh(user)
    
    return user

async def get_users_to_rate(session: AsyncSession, event_id: int, rater_id: int) -> List[User]:
    """
    Получает список пользователей, которых можно оценить в рамках мероприятия.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        event_id: ID мероприятия
        rater_id: ID пользователя, который оценивает
    
    Returns:
        Список объектов пользователей
    """
    # Получаем всех участников мероприятия, кроме самого оценивающего
    stmt = (
        select(User)
        .join(event_participants, User.id == event_participants.c.user_id)
        .where(
            and_(
                event_participants.c.event_id == event_id,
                User.id != rater_id,
                not_(
                    select(Rating.id).exists()
                    .where(
                        and_(
                            Rating.event_id == event_id,
                            Rating.rater_id == rater_id,
                            Rating.rated_id == User.id
                        )
                    )
                )
            )
        )
    )
    
    result = await session.execute(stmt)
    return result.scalars().all()