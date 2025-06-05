import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# ИСПРАВЛЕНО: Убран хардкод токена из кода
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения! Создайте файл .env с вашим токеном.")

# ИСПРАВЛЕНО: Правильная логика получения DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Локальная база данных по умолчанию
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/yasami_bot"
    print("⚠️ Используется локальная база данных по умолчанию")
else:
    # Исправляем URL для Railway и других сервисов
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Настройки для webhook
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", f"/webhook/{BOT_TOKEN}")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", f"{WEBHOOK_HOST}{WEBHOOK_PATH}")

# Настройки веб-сервера
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "localhost")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8000))

# Пути к ресурсам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Настройки для системы рейтинга
DEFAULT_RATING = 100  # Начальный рейтинг пользователя
MIN_RATING_TO_CREATE = 20  # Минимальный рейтинг для создания мероприятий
MIN_RATING_TO_VIEW = 0  # Минимальный рейтинг для просмотра мероприятий

# Стоимость VIP в токенах
VIP_COST = 1500

# Настройки для рейтинга
RATING_IMPACT = {
    1: -10,  # Одна звезда: -10 к рейтингу
    2: -5,   # Две звезды: -5 к рейтингу
    3: 0,    # Три звезды: без изменений
    4: 5,    # Четыре звезды: +5 к рейтингу
    5: 10    # Пять звезд: +10 к рейтингу
}

# РАСШИРЕННЫЙ список популярных городов России
POPULAR_CITIES = [
    # Миллионники
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Красноярск",
    "Самара",
    "Уфа",
    "Ростов-на-Дону",
    "Краснодар",
    "Омск",
    "Воронеж",
    "Пермь",
    "Волгоград",
    
    # Крупные города
    "Саратов",
    "Тюмень",
    "Тольятти",
    "Ижевск",
    "Барнаул",
    "Ульяновск",
    "Иркутск",
    "Хабаровск",
    "Ярославль",
    "Владивосток",
    "Махачкала",
    "Томск",
    "Оренбург",
    "Кемерово",
    "Новокузнецк",
    "Рязань",
    "Астрахань",
    "Пенза",
    "Липецк",
    "Тула",
    "Киров",
    "Чебоксары",
    "Калининград",
    "Брянск",
    "Курск",
    "Иваново",
    "Магнитогорск",
    "Тверь",
    "Ставрополь",
    "Сочи",
    
    # Дополнительные важные города
    "Белгород",
    "Архангельск",
    "Владимир",
    "Сургут",
    "Калуга",
    "Смоленск",
    "Волжский",
    "Курган",
    "Череповец",
    "Вологда",
    "Орёл",
    "Подольск",
    "Саранск",
    "Стерлитамак",
    "Петрозаводск",
    "Нижневартовск",
    "Йошкар-Ола",
    "Мурманск",
    "Тамбов",
    "Ставрополь",
    "Комсомольск-на-Амуре",
    "Якутск",
    "Таганрог",
    "Братск",
    "Дзержинск",
    "Сыктывкар",
    "Орск",
    "Нижнекамск",
    "Ангарск",
    "Балаково",
    "Благовещенск",
    "Псков",
    "Великий Новгород",
    "Энгельс",
    "Старый Оскол",
    "Бийск"
]

# Настройки для уведомлений
NOTIFICATION_SETTINGS = {
    "event_reminder_hours": 2,  # За сколько часов напоминать о мероприятии
    "rating_reminder_days": 1,  # Через сколько дней напоминать об оценке
}

# Настройки для модерации
MODERATION_SETTINGS = {
    "max_event_title_length": 100,
    "max_event_description_length": 1000,
    "max_about_length": 500,
    "min_event_time_advance_hours": 1,  # Минимум за час до создания мероприятия
}

# Настройки безопасности
SECURITY_SETTINGS = {
    "max_events_per_day": 5,  # Максимум мероприятий в день для одного пользователя
    "max_registrations_per_day": 10,  # Максимум регистраций в день
}
