FROM python:3.11-slim

WORKDIR /app

# Установить зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать код приложения
COPY app ./app

# Переменная окружения для порта
ENV PORT=8000

# Expose порт
EXPOSE 8000

# Запустить приложение
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
