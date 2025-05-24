from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from database.models import User, Event, EventPurpose, EventTargetAudience, event_participants

async def create_event(session: AsyncSession, creator_id: int, title: str, city: str, 
                      purpose: EventPurpose, target_audience: EventTargetAudience, 
                      description: str, event_date: datetime, min_age: int = None, 
                      max_age: int = None, max_participants: int = None) -> Event:
    """
    Создает новое мероприятие.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        creator_id: ID создателя мероприятия
        title: Название мероприятия
        city: Город проведения
        purpose: Цель мероприятия (из перечисления EventPurpose)
        target_audience: Целевая аудитория (из перечисления EventTargetAudience)
        description: Описание мероприятия
        event_date: Дата и время проведения
        min_age: Минимальный возраст участников (опционально)
        max_age: Максимальный возраст участников (опционально)
        max_participants: Максимальное количество участников (опционально)
    
    Returns:
        Созданный объект мероприятия
    """
    event = Event(
        creator_id=creator_id,
        title=title,
        city=city,
        purpose=purpose,
        target_audience=target_audience,
        min_age=min_age,
        max_age=max_age,
        description=description,
        event_date=event_date,
        max_participants=max_participants,
        is_hidden=False
    )
    
    session.add(event)
    await session.commit()
    await session.refresh(event)
    
    return event

async def get_events_by_city(session: AsyncSession, city: str) -> List[Event]:
    """
    Получает список мероприятий в указанном городе.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        city: Название города
    
    Returns:
        Список объектов мероприятий
    """
    result = await session.execute(
        select(Event)
        .where(
            and_(
                Event.city == city,
                Event.event_date > datetime.now(),
                Event.is_hidden == False
            )
        )
        .order_by(Event.event_date)
    )
    return result.scalars().all()

async def get_event_by_id(session: AsyncSession, event_id: int) -> Optional[Event]:
    """
    Получает мероприятие по его ID.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        event_id: ID мероприятия
    
    Returns:
        Объект мероприятия или None, если мероприятие не найдено
    """
    result = await session.execute(select(Event).where(Event.id == event_id))
    return result.scalars().first()

async def register_for_event(session: AsyncSession, user_id: int, event_id: int) -> Tuple[bool, str]:
    """
    Регистрирует пользователя на мероприятие.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        event_id: ID мероприятия
    
    Returns:
        Tuple с результатом:
        - Первый элемент: успешность операции (True/False)
        - Второй элемент: сообщение об успехе или ошибке
    """
    # Получаем мероприятие
    event = await get_event_by_id(session, event_id)
    
    if not event:
        return False, "Мероприятие не найдено"
    
    # Проверяем, не заполнено ли мероприятие
    if event.is_full:
        return False, "Мероприятие уже заполнено"
    
    # Получаем пользователя
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return False, "Пользователь не найден"
    
    # Проверяем, подходит ли пользователь по критериям
    if event.min_age and user.age < event.min_age:
        return False, f"Минимальный возраст для участия: {event.min_age} лет"
    
    if event.max_age and user.age > event.max_age:
        return False, f"Максимальный возраст для участия: {event.max_age} лет"
    
    if event.target_audience == EventTargetAudience.MALE and user.gender != Gender.MALE:
        return False, "Мероприятие только для мужчин"
    
    if event.target_audience == EventTargetAudience.FEMALE and user.gender != Gender.FEMALE:
        return False, "Мероприятие только для женщин"
    
    # Проверяем, не зарегистрирован ли пользователь уже
    result = await session.execute(
        select(event_participants).where(
            and_(
                event_participants.c.user_id == user_id,
                event_participants.c.event_id == event_id
            )
        )
    )
    if result.first():
        return False, "Вы уже зарегистрированы на это мероприятие"
    
    # Регистрируем пользователя
    stmt = event_participants.insert().values(user_id=user_id, event_id=event_id)
    await session.execute(stmt)
    await session.commit()
    
    return True, "Вы успешно зарегистрировались на мероприятие"

async def unregister_from_event(session: AsyncSession, user_id: int, event_id: int) -> Tuple[bool, str]:
    """
    Отменяет регистрацию пользователя на мероприятие.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        event_id: ID мероприятия
    
    Returns:
        Tuple с результатом:
        - Первый элемент: успешность операции (True/False)
        - Второй элемент: сообщение об успехе или ошибке
    """
    # Проверяем, зарегистрирован ли пользователь на мероприятие
    result = await session.execute(
        select(event_participants).where(
            and_(
                event_participants.c.user_id == user_id,
                event_participants.c.event_id == event_id
            )
        )
    )
    if not result.first():
        return False, "Вы не зарегистрированы на это мероприятие"
    
    # Отменяем регистрацию
    stmt = event_participants.delete().where(
        and_(
            event_participants.c.user_id == user_id,
            event_participants.c.event_id == event_id
        )
    )
    await session.execute(stmt)
    await session.commit()
    
    return True, "Вы успешно отменили регистрацию на мероприятие"

async def get_events_to_rate(session: AsyncSession, user_id: int) -> List[Event]:
    """
    Получает список мероприятий, которые пользователь посетил, но еще не оценил всех участников.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
    
    Returns:
        Список объектов мероприятий
    """
    # Получаем мероприятия, в которых участвовал пользователь и которые уже прошли
    result = await session.execute(
        select(Event)
        .join(event_participants, Event.id == event_participants.c.event_id)
        .where(
            and_(
                event_participants.c.user_id == user_id,
                Event.event_date < datetime.now()
            )
        )
    )
    
    return result.scalars().all()