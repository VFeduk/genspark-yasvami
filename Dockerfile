FROM python:3.11-slim

# Устанавливаем переменные среды
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Moscow

# Устанавливаем базовые зависимости системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Указываем переменные окружения, которые будут заменены значениями из Railway
ENV BOT_TOKEN=${BOT_TOKEN}
ENV DATABASE_URL=${DATABASE_URL}

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["python", "main.py"]
