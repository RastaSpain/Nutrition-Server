# Nutrition Management System - Shopping List Feature

## 🎯 Что добавлено

### Shopping List Generation
Автоматическая генерация списков покупок на основе планов питания.

## 📁 Структура

```
nutrition-server/
├── app/
│   ├── main.py                           # FastAPI app
│   ├── routers/
│   │   ├── health.py                     # Health check
│   │   ├── nutrition_router.py           # Nutrition endpoints (stub)
│   │   └── shopping_list_router.py       # Shopping List endpoints ✨ NEW
│   ├── services/
│   │   └── shopping_list.py              # Shopping List service ✨ NEW
│   └── models/
│       └── shopping_list_schemas.py      # Pydantic models ✨ NEW
├── requirements.txt
└── README.md
```

## 🚀 API Endpoints

### POST /api/nutrition/shopping-list/generate
Генерирует список покупок для плана питания

**Request:**
```json
{
  "meal_plan_id": "recnd7GzJqTkiBTWa",
  "shopping_date": "2024-12-30"
}
```

**Response:**
```json
{
  "shopping_list_id": "rec123456789",
  "meal_plan_id": "recnd7GzJqTkiBTWa",
  "items_count": 15,
  "total_recipes": 20,
  "total_meals": 35,
  "message": "Shopping list generated successfully"
}
```

### GET /api/nutrition/shopping-list/{shopping_list_id}
Получает детальную информацию о списке покупок

**Response:**
```json
{
  "shopping_list_id": "rec123456789",
  "list_name": "Shopping List - Test Plan (2024-12-30)",
  "status": "Pending",
  "shopping_date": "2024-12-30",
  "total_cost": null,
  "items_count": 15,
  "items": [...]
}
```

## 🔧 Как работает Shopping List Generation

### Процесс:

1. **Получение плана питания**
   - Находит план по ID
   - Получает все запланированные приёмы пищи (Planned_Meals)

2. **Сбор рецептов**
   - Извлекает уникальные recipe_ids из всех приёмов пищи
   - Учитывает количество порций (Servings) для каждого приёма

3. **Сбор ингредиентов**
   - Получает Recipe_Ingredients для всех рецептов
   - Умножает количество ингредиентов на количество порций
   - Получает названия ингредиентов из таблицы Ingredients

4. **Агрегация**
   - Группирует одинаковые ингредиенты (по ingredient_id + unit)
   - Суммирует количество
   - Сортирует по названию

5. **Создание Shopping List**
   - Создаёт запись в таблице Shopping_Lists
   - Создаёт записи в Shopping_List_Items (batch операция)
   - Связывает с ингредиентами

### Пример агрегации:

```
Meal 1: Pollo Batch (250g) - 2 порции
Meal 2: Chicken Rice (250g) - 1 порция

Recipe: Pollo Batch
- Pollo: 120g/порция

Итого: 120g × 2 + 120g × 1 = 360g pollo
```

## 🏗️ Деплой на Railway

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
```
AIRTABLE_API_KEY=pat...
```

### 3. Запуск
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Railway Config
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 📊 Airtable Schema

### Shopping_Lists
- List Name (text)
- User (link to Users)
- Meal Plan (link to Meal_Plans)
- Shopping Date (date)
- Status (select: Pending/Completed)
- Total Cost (EUR) (currency)
- Notes (long text)
- Shopping_List_Items (link)

### Shopping_List_Items
- Item (text) - название + количество
- Shopping List (link)
- Ingredient (link to Ingredients)
- Quantity (number)
- Unit (select: г/мл/шт)
- Purchased (checkbox)
- Price (EUR) (currency)

## 🧪 Тестирование

### 1. Health Check
```bash
curl https://your-url.railway.app/health
```

### 2. Generate Shopping List
```bash
curl -X POST https://your-url.railway.app/api/nutrition/shopping-list/generate \
  -H "Content-Type: application/json" \
  -d '{
    "meal_plan_id": "recnd7GzJqTkiBTWa",
    "shopping_date": "2024-12-30"
  }'
```

### 3. Get Shopping List
```bash
curl https://your-url.railway.app/api/nutrition/shopping-list/{id}
```

## 🔗 n8n Integration

Workflow "Claud Test" уже настроен:

```
Webhook → Generate Shopping List
```

Нужно только **подключить** второй node к цепочке:

1. Открыть workflow "Claud Test"
2. Соединить "Запрос к Python Серверу" → "Generate Shopping List"
3. Сохранить и протестировать

## 🎯 Next Steps

1. ✅ Деплой обновлённого кода на Railway
2. ✅ Тестирование Shopping List generation
3. ⚠️ Подключить node в n8n workflow
4. 🔜 Добавить категоризацию ингредиентов (Mercadona sections)
5. 🔜 Добавить ценовые данные
6. 🔜 Telegram уведомления о списке покупок

## 📝 Notes

- Batch операции используются для оптимизации (10 records/batch)
- Агрегация учитывает unit (г/мл/шт)
- Shopping List автоматически связывается с Meal Plan
- Items автоматически связываются с Ingredients

## 🐛 Troubleshooting

**Ошибка: "Meal plan not found"**
- Проверь meal_plan_id
- Проверь доступ к Airtable

**Ошибка: "No planned meals found"**
- Убедись что в плане есть Planned_Meals
- Проверь связи Recipe в Planned_Meals

**Пустой список ингредиентов**
- Проверь Recipe_Ingredients для рецептов
- Убедись что есть связь Ingredients
