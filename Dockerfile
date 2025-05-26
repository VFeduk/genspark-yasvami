FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Явно указываем переменные окружения, которые будут заменены значениями из Railway
ENV BOT_TOKEN=${BOT_TOKEN}
ENV DATABASE_URL=${DATABASE_URL}

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["python", "main.py"]
