from datetime import datetime
from typing import Tuple, Optional

def validate_age(age_str: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Валидация введенного возраста.
    
    Args:
        age_str: Строка с возрастом
    
    Returns:
        Tuple с результатом валидации:
        - Первый элемент: успешность валидации (True/False)
        - Второй элемент: возраст как число, если валидация успешна, иначе None
        - Третий элемент: сообщение об ошибке, если валидация не удалась, иначе None
    """
    try:
        age = int(age_str.strip())
        
        if age < 14:
            return False, None, "Минимальный возраст для пользователей бота - 14 лет."
        
        if age > 100:
            return False, None, "Пожалуйста, введите реальный возраст (не более 100 лет)."
        
        return True, age, None
    except ValueError:
        return False, None, "Пожалуйста, введите корректный возраст (число)."

def validate_event_datetime(datetime_str: str) -> Tuple[bool, Optional[datetime], Optional[str]]:
    """
    Валидация введенной даты и времени мероприятия.
    
    Args:
        datetime_str: Строка с датой и временем в формате ДД.ММ.ГГГГ ЧЧ:ММ
    
    Returns:
        Tuple с результатом валидации:
        - Первый элемент: успешность валидации (True/False)
        - Второй элемент: объект datetime, если валидация успешна, иначе None
        - Третий элемент: сообщение об ошибке, если валидация не удалась, иначе None
    """
    try:
        event_datetime = datetime.strptime(datetime_str.strip(), "%d.%m.%Y %H:%M")
        
        if event_datetime < datetime.now():
            return False, None, "Нельзя создать мероприятие в прошлом. Пожалуйста, укажите дату и время в будущем."
        
        return True, event_datetime, None
    except ValueError:
        return False, None, "Неверный формат даты и времени. Пожалуйста, укажите в формате ДД.ММ.ГГГГ ЧЧ:ММ, например: 15.06.2025 18:00"

def validate_city(city: str, popular_cities: list) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Валидация введенного города.
    
    Args:
        city: Название города
        popular_cities: Список популярных городов для проверки
    
    Returns:
        Tuple с результатом валидации:
        - Первый элемент: успешность валидации (True/False)
        - Второй элемент: нормализованное название города, если валидация успешна, иначе None
        - Третий элемент: сообщение об ошибке, если валидация не удалась, иначе None
    """
    city = city.strip().title()
    
    if len(city) < 2:
        return False, None, "Название города слишком короткое. Пожалуйста, введите корректное название."
    
    # Простая нормализация названия города
    normalized_city = " ".join(city.split())
    
    # Здесь можно добавить проверку по базе городов или по API
    # Для простоты просто проверяем на корректность ввода
    
    return True, normalized_city, None