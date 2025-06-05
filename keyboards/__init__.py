# Исправленный keyboards/__init__.py
# Объединяем все клавиатуры в единой точке импорта

from .main_menu import (
    get_start_keyboard,
    get_main_menu_keyboard, 
    get_city_keyboard,
    get_gender_keyboard,
    get_profile_keyboard,
    get_edit_profile_keyboard,
    get_payment_methods_keyboard,
    get_knowledge_keyboard,
    get_rating_keyboard,
    get_stars_keyboard
)

# ИСПРАВЛЕНО: Импорт из правильного файла event_creation.py
from .event_creation import (
    get_event_creation_rules_keyboard,
    get_confirmation_keyboard,
    get_event_purpose_keyboard,
    get_event_target_audience_keyboard,
    get_event_age_keyboard,
    get_event_registration_keyboard
)

__all__ = [
    # Main menu keyboards
    'get_start_keyboard',
    'get_main_menu_keyboard',
    'get_city_keyboard', 
    'get_gender_keyboard',
    'get_profile_keyboard',
    'get_edit_profile_keyboard',
    'get_payment_methods_keyboard',
    'get_knowledge_keyboard',
    'get_rating_keyboard',
    'get_stars_keyboard',
    
    # Event creation keyboards  
    'get_event_creation_rules_keyboard',
    'get_confirmation_keyboard',
    'get_event_purpose_keyboard',
    'get_event_target_audience_keyboard',
    'get_event_age_keyboard',
    'get_event_registration_keyboard'
]
