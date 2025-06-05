from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# ИСПРАВЛЕНО: Импортируем Base из db.py вместо создания нового
from .db import Base

# Промежуточная таблица для отношения многие-ко-многим между пользователями и мероприятиями
event_participants = Table(
    "event_participants",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("event_id", Integer, ForeignKey("events.id")),
    Column("registration_time", DateTime, default=func.now())
)

# Перечисления для различных полей
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    ANY = "any"

class EventPurpose(str, Enum):
    WALK = "walk"  # Пошли гулять
    MEET = "meet"  # Давайте знакомиться
    TRAVEL = "travel"  # Совместные поездки/путешествия
    HELP = "help"  # Друзья мне нужна помощь
    PARTY = "party"  # Пойдем тусить

class EventTargetAudience(str, Enum):
    MALE = "male"  # Только для мужчин
    FEMALE = "female"  # Только для женщин
    ALL = "all"  # Для всех

class UserType(str, Enum):
    REGULAR = "regular"  # Обычный пользователь
    VIP = "vip"  # VIP-пользователь

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    city = Column(String)
    display_name = Column(String)  # Имя, которое показывается в профиле
    age = Column(Integer)
    gender = Column(SQLEnum(Gender))
    about = Column(Text, nullable=True)
    rating = Column(Integer, default=100)  # Рейтинг пользователя, по умолчанию 100
    tokens = Column(Integer, default=0)  # Количество токенов
    user_type = Column(SQLEnum(UserType), default=UserType.REGULAR)
    vip_until = Column(DateTime, nullable=True)  # Срок действия VIP-статуса
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Отношения
    created_events = relationship("Event", back_populates="creator")
    participated_events = relationship(
        "Event", 
        secondary=event_participants, 
        back_populates="participants"
    )
    given_ratings = relationship("Rating", foreign_keys="[Rating.rater_id]", back_populates="rater")
    received_ratings = relationship("Rating", foreign_keys="[Rating.rated_id]", back_populates="rated")
    transactions = relationship("Transaction", back_populates="user")

    @property
    def is_vip(self):
        if self.user_type != UserType.VIP:
            return False
        if not self.vip_until:
            return False
        return self.vip_until > datetime.now()
    
    def activate_vip(self, duration_days=30):
        """Активировать VIP-статус"""
        self.user_type = UserType.VIP
        if self.vip_until and self.vip_until > datetime.now():
            # Если VIP уже активен, добавляем к текущему сроку
            self.vip_until += timedelta(days=duration_days)
        else:
            # Иначе устанавливаем новый срок
            self.vip_until = datetime.now() + timedelta(days=duration_days)
    
    def can_create_events(self):
        """Проверка возможности создавать мероприятия"""
        from config import MIN_RATING_TO_CREATE
        return self.rating >= MIN_RATING_TO_CREATE
    
    def can_view_events(self):
        """Проверка возможности просматривать мероприятия"""
        from config import MIN_RATING_TO_VIEW
        return self.rating >= MIN_RATING_TO_VIEW

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    city = Column(String, nullable=False)
    purpose = Column(SQLEnum(EventPurpose), nullable=False)
    target_audience = Column(SQLEnum(EventTargetAudience), nullable=False)
    min_age = Column(Integer, nullable=True)  # Минимальный возраст участников
    max_age = Column(Integer, nullable=True)  # Максимальный возраст участников
    description = Column(Text, nullable=False)
    event_date = Column(DateTime, nullable=False)
    max_participants = Column(Integer, nullable=True)  # Максимальное количество участников
    is_hidden = Column(Boolean, default=False)  # Скрыто ли мероприятие (для VIP)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Отношения
    creator = relationship("User", back_populates="created_events")
    participants = relationship(
        "User", 
        secondary=event_participants, 
        back_populates="participated_events"
    )
    ratings = relationship("Rating", back_populates="event")
    
    @property
    def is_full(self):
        """Проверка, заполнено ли мероприятие"""
        if not self.max_participants:
            return False
        return len(self.participants) >= self.max_participants
    
    def can_register(self, user):
        """ИСПРАВЛЕНО: Проверка возможности регистрации пользователя"""
        if self.is_full:
            return False
        
        # Проверка, не является ли пользователь создателем
        if self.creator_id == user.id:
            return False
            
        # Проверка, не зарегистрирован ли уже
        if user in self.participants:
            return False
        
        # Проверка по возрасту
        if self.min_age and user.age and user.age < self.min_age:
            return False
        if self.max_age and user.age and user.age > self.max_age:
            return False
        
        # Проверка по полу
        if self.target_audience == EventTargetAudience.MALE and user.gender != Gender.MALE:
            return False
        if self.target_audience == EventTargetAudience.FEMALE and user.gender != Gender.FEMALE:
            return False
        
        return True

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    rater_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rated_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)  # Оценка от 1 до 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Отношения
    event = relationship("Event", back_populates="ratings")
    rater = relationship("User", foreign_keys=[rater_id], back_populates="given_ratings")
    rated = relationship("User", foreign_keys=[rated_id], back_populates="received_ratings")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # Сумма транзакции (может быть положительной или отрицательной)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # ИСПРАВЛЕНО: Добавлен back_populates
    user = relationship("User", back_populates="transactions")
