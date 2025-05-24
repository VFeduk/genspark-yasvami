from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional

from database.models import Event

def get_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для первого приветственного сообщения"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="СТАРТ", callback_data="start_button")]
    ])
    return keyboard

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Основная клавиатура главного меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мой профиль", callback_data="profile")],
        [InlineKeyboardButton(text="Создать мероприятие", callback_data="create_event")],
        [InlineKeyboardButton(text="Посмотреть мероприятия", callback_data="view_events")],
        [InlineKeyboardButton(text="База знаний", callback_data="knowledge")]
    ])
    return keyboard

def get_city_keyboard(cities: list, include_current: bool = False, current_city: str = None) -> InlineKeyboardMarkup:
    """Клавиатура для выбора города"""
    buttons = []
    
    # Если нужно, добавляем кнопку с текущим городом
    if include_current and current_city:
        buttons.append([InlineKeyboardButton(text=f"Оставить: {current_city}", callback_data=f"city_{current_city}")])
    
    # Добавляем кнопки с городами
    city_buttons = []
    for i, city in enumerate(cities):
        city_buttons.append(InlineKeyboardButton(text=city, callback_data=f"city_{city}"))
        
        # По 2 города в ряд
        if (i + 1) % 2 == 0 or i == len(cities) - 1:
            buttons.append(city_buttons)
            city_buttons = []
    
    # Добавляем кнопку "Другой город"
    buttons.append([InlineKeyboardButton(text="Другой город", callback_data="other_city")])
    
    # Добавляем кнопку "Назад"
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора пола"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data="gender_male")],
        [InlineKeyboardButton(text="Женский", callback_data="gender_female")]
    ])
    return keyboard

def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для профиля пользователя"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Редактировать профиль", callback_data="edit_profile")],
        [InlineKeyboardButton(text="Мои мероприятия", callback_data="my_events")],
        [InlineKeyboardButton(text="Купить VIP", callback_data="buy_vip")],
        [InlineKeyboardButton(text="Пополнить токены", callback_data="add_tokens")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ])
    return keyboard

def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для редактирования профиля"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить город", callback_data="edit_city")],
        [InlineKeyboardButton(text="Изменить имя", callback_data="edit_name")],
        [InlineKeyboardButton(text="Изменить возраст", callback_data="edit_age")],
        [InlineKeyboardButton(text="Изменить информацию о себе", callback_data="edit_about")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_profile")]
    ])
    return keyboard

def get_payment_methods_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора способа оплаты"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Банковская карта", callback_data="payment_card")],
        [InlineKeyboardButton(text="Электронные кошельки", callback_data="payment_wallet")],
        [InlineKeyboardButton(text="Мобильный платеж", callback_data="payment_mobile")],
        [InlineKeyboardButton(text="Отмена", callback_data="back_to_profile")]
    ])
    return keyboard

def get_knowledge_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для базы знаний"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Правила создания мероприятий", callback_data="knowledge_creation")],
        [InlineKeyboardButton(text="Правила регистрации на мероприятие", callback_data="knowledge_registration")],
        [InlineKeyboardButton(text="О системе рейтинга", callback_data="knowledge_rating")],
        [InlineKeyboardButton(text="О VIP-статусе", callback_data="knowledge_vip")],
        [InlineKeyboardButton(text="О проекте", callback_data="knowledge_about")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ])
    return keyboard

def get_rating_keyboard(events: List[Event]) -> InlineKeyboardMarkup:
    """Клавиатура для выбора мероприятия для оценки"""
    buttons = []
    
    for event in events:
        # Сокращаем название, если оно слишком длинное
        event_name = event.title[:30] + "..." if len(event.title) > 30 else event.title
        event_date = event.event_date.strftime("%d.%m.%Y")
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{event_name} ({event_date})",
                callback_data=f"rate_event_{event.id}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_stars_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора оценки (звезд)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐", callback_data="rate_1"),
            InlineKeyboardButton(text="⭐⭐", callback_data="rate_2"),
            InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3"),
            InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4"),
            InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5")
        ]
    ])
    return keyboard