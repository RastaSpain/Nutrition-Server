# 🍽️ Nutrition Server

Backend сервер для системы управления питанием. FastAPI + Airtable.

## 🚀 Быстрый старт

### 1. Установка локально (для тестирования)

```bash
# Клонировать репозиторий (если используешь Git)
git clone <your-repo-url>
cd nutrition-server

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env

# Редактировать .env и добавить свой AIRTABLE_API_KEY
nano .env  # или любой редактор
```

### 2. Настройка переменных окружения

Открой `.env` и укажи:

```env
AIRTABLE_API_KEY=patXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appBgJb1hzG4vFT1b
PORT=8000
```

**Где взять AIRTABLE_API_KEY:**
1. Зайди на https://airtable.com/create/tokens
2. Create new token → "Nutrition Server"
3. Scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
4. Access: выбери базу `appBgJb1hzG4vFT1b`
5. Скопируй токен

### 3. Запуск локально

```bash
# Из корня проекта
python -m app.main

# Или через uvicorn напрямую
uvicorn app.main:app --reload --port 8000
```

Сервер запустится на `http://localhost:8000`

### 4. Проверка работы

Открой в браузере:
- **Документация API:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
- **Root:** http://localhost:8000/

## 📡 API Endpoints

### Health Check
```
GET /health
```
Проверяет работу сервера и подключение к Airtable.

### Создать план питания
```
POST /api/nutrition/meal-plan/create

Body:
{
  "user_id": "recw1ls8WIo31cteD",
  "week_start": "2025-12-29",
  "plan_name": "Week 1",
  "notes": "Optional notes"
}

Response:
{
  "meal_plan_id": "recXXXXXXXXXXXXXX",
  "plan_name": "Week 1",
  "week_start": "2025-12-29",
  "week_end": "2026-01-04",
  "total_meals": 35,
  "avg_calories": 2750,
  "avg_protein": 210,
  "status": "success",
  "message": "План питания создан! 35 приёмов пищи добавлено."
}
```

### Получить план питания
```
GET /api/nutrition/meal-plan/{plan_id}
```

### Генерация списка покупок
```
POST /api/nutrition/shopping-list/generate

Body:
{
  "meal_plan_id": "recXXXXXXXXXXXXXX"
}
```
(В разработке)

## 🐳 Деплой на Railway

### Вариант 1: Через GitHub

1. **Создай GitHub репозиторий:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Деплой на Railway:**
   - Зайди на https://railway.app
   - "New Project" → "Deploy from GitHub repo"
   - Выбери свой репозиторий
   - Railway автоматически обнаружит Dockerfile

3. **Настрой переменные окружения в Railway:**
   - Settings → Variables
   - Добавь `AIRTABLE_API_KEY`
   - Добавь `AIRTABLE_BASE_ID` (если нужен другой)

4. **Деплой!**
   - Railway автоматически задеплоит
   - Получишь URL: `https://your-app.up.railway.app`

### Вариант 2: Без GitHub (из ZIP)

1. Создай ZIP архив проекта
2. Railway → "Deploy" → "From Local"
3. Загрузи ZIP
4. Настрой переменные окружения
5. Деплой!

## 🧪 Тестирование

### Локально через curl:

```bash
# Health check
curl http://localhost:8000/health

# Создать план питания
curl -X POST http://localhost:8000/api/nutrition/meal-plan/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "recw1ls8WIo31cteD",
    "week_start": "2025-12-29"
  }'
```

### Через n8n:

**1. HTTP Request Node:**
- Method: POST
- URL: `https://your-server.railway.app/api/nutrition/meal-plan/create`
- Body (JSON):
```json
{
  "user_id": "recw1ls8WIo31cteD",
  "week_start": "2025-12-29",
  "plan_name": "My Week"
}
```

**2. Обработать ответ в n8n**

## 📂 Структура проекта

```
nutrition-server/
├── app/
│   ├── main.py              # FastAPI приложение
│   ├── routers/
│   │   ├── health.py        # Health check endpoints
│   │   └── nutrition.py     # Nutrition endpoints
│   ├── services/
│   │   ├── airtable.py      # Airtable интеграция
│   │   └── meal_planner.py  # Логика планирования
│   └── models/
│       └── schemas.py       # Pydantic модели
├── requirements.txt         # Python зависимости
├── Dockerfile              # Docker контейнер
├── .env.example            # Пример переменных окружения
├── .gitignore              # Git ignore файл
└── README.md               # Этот файл
```

## 🔧 Технологии

- **FastAPI** - современный веб-фреймворк
- **pyairtable** - официальный Python клиент для Airtable
- **pydantic** - валидация данных
- **uvicorn** - ASGI сервер
- **Docker** - контейнеризация

## 📝 Логика работы

1. **n8n** вызывает endpoint `/api/nutrition/meal-plan/create`
2. **Сервер**:
   - Получает все рецепты из Airtable
   - Генерирует оптимальный план на 7 дней
   - Создаёт запись в `Meal_Plans`
   - Создаёт 35 записей в `Planned_Meals` (батчами по 10)
   - Возвращает результат
3. **n8n** получает ответ с `meal_plan_id`

**Скорость:** ~2-3 секунды на создание полного плана!

## 🐛 Отладка

### Проверка подключения к Airtable:
```bash
curl http://localhost:8000/health
```

Должен вернуть:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "airtable_connected": true
}
```

### Логи в Railway:
- Dashboard → Your Project → Deployments → Logs

## 🚀 Что дальше?

- [ ] Добавить генерацию shopping lists
- [ ] Добавить batch cooking schedule
- [ ] Оптимизация плана по бюджету
- [ ] ML рекомендации блюд
- [ ] Интеграция с Amazon для Amazon проекта

## 📞 Поддержка

Проблемы? Создай issue или спроси Claude! 😊
