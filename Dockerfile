# Базовий образ
FROM python:3.9-slim

# Встановлюємо залежності
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код додатку
COPY ./app /app

# Встановлюємо робочу директорію
WORKDIR /app

# Відкриваємо порт
EXPOSE 8000

# Запускаємо додаток
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
