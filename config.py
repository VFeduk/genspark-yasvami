import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота Telegram с запасным вариантом для отладки
BOT_TOKEN = os.getenv("BOT_TOKEN", "8118843770:AAHRFDNRFeW2mbFctEUdM82p9mAeRj73b78")

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/yasami_bot")

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/yasami_bot")

# Настройки для webhook, если потребуется
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

# Список популярных городов для быстрого выбора
POPULAR_CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Новокузнецк",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Красноярск",
    "Самара"
]
