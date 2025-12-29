# 🚀 Deployment Guide - Shopping List Feature

## Шаг 1: Подготовка кода

### 1.1 Коммит в GitHub

```bash
cd Nutrition-Server

# Добавляем новые файлы
git add .

# Коммитим изменения
git commit -m "feat: Add Shopping List generation endpoint

- Added ShoppingListService for generating shopping lists
- Added shopping_list_router with POST /api/nutrition/shopping-list/generate
- Added GET /api/nutrition/shopping-list/{id} endpoint
- Implemented ingredient aggregation with servings calculation
- Added batch operations for Shopping_List_Items creation"

# Пушим в GitHub
git push origin main
```

### 1.2 Проверка файлов

Убедись что все файлы на месте:
```
✅ app/services/shopping_list.py
✅ app/routers/shopping_list_router.py
✅ app/models/shopping_list_schemas.py
✅ app/main.py (обновлён)
✅ requirements.txt
✅ README.md
```

## Шаг 2: Railway Deployment

Railway автоматически задеплоит новый код из GitHub.

### 2.1 Проверь статус деплоя

1. Открой https://railway.app
2. Проект: `nutrition-server`
3. Environment: `production`
4. Вкладка: `Deployments`

Статус должен быть: `✅ Success`

### 2.2 Проверь логи

```
Вкладка "Logs"
```

Должны увидеть:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2.3 Проверь Variables

```
Вкладка "Variables"
```

Должно быть:
```
AIRTABLE_API_KEY = pat...
PORT = 8000 (автоматически)
```

## Шаг 3: Тестирование

### 3.1 Health Check

```bash
curl https://nutrition-server-production-7959.up.railway.app/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "airtable_connection": "ok",
  "base_accessible": true,
  "recipes_count": 1
}
```

### 3.2 Swagger UI

Открой в браузере:
```
https://nutrition-server-production-7959.up.railway.app/docs
```

Должны увидеть новые endpoints:
- `POST /api/nutrition/shopping-list/generate`
- `GET /api/nutrition/shopping-list/{shopping_list_id}`

### 3.3 Тест Shopping List Generation

**Через Swagger UI:**

1. Открой `POST /api/nutrition/shopping-list/generate`
2. Нажми "Try it out"
3. Вставь JSON:
```json
{
  "meal_plan_id": "recnd7GzJqTkiBTWa",
  "shopping_date": "2024-12-30"
}
```
4. Нажми "Execute"

**Через curl:**
```bash
curl -X POST \
  https://nutrition-server-production-7959.up.railway.app/api/nutrition/shopping-list/generate \
  -H "Content-Type: application/json" \
  -d '{
    "meal_plan_id": "recnd7GzJqTkiBTWa",
    "shopping_date": "2024-12-30"
  }'
```

**Ожидаемый ответ:**
```json
{
  "shopping_list_id": "rec...",
  "meal_plan_id": "recnd7GzJqTkiBTWa",
  "items_count": 15,
  "total_recipes": 20,
  "total_meals": 35,
  "message": "Shopping list generated successfully"
}
```

### 3.4 Проверка в Airtable

1. Открой Airtable базу `База рецептов`
2. Таблица `Shopping_Lists` - должна появиться новая запись
3. Таблица `Shopping_List_Items` - должны быть items

## Шаг 4: n8n Integration

### 4.1 Обновление workflow "Claud Test"

1. Открой n8n: https://torgsale.app.n8n.cloud
2. Workflow: "Claud Test"
3. Соедини nodes:
   ```
   "Запрос к Python Серверу" → "Generate Shopping List"
   ```
4. Сохрани workflow

### 4.2 Тестирование через n8n

**Вариант A: Через Webhook**
```bash
curl https://torgsale.app.n8n.cloud/webhook/79edc9a8-8f0c-4a44-87fa-85cd16b38292
```

**Вариант B: Manual execution**
1. Открой workflow
2. Нажми "Execute Workflow"
3. Проверь результаты

## Шаг 5: Проверка результатов

### 5.1 В Airtable

**Shopping_Lists:**
- ✅ List Name: "Shopping List - Test Manual Date (2024-12-30)"
- ✅ Meal Plan: linked to meal plan
- ✅ Status: "Pending"
- ✅ Shopping Date: "2024-12-30"

**Shopping_List_Items:**
- ✅ Все items созданы
- ✅ Ingredient links работают
- ✅ Quantities правильные
- ✅ Units правильные

### 5.2 В Railway Logs

```
INFO: Generating shopping list for meal plan: recnd7GzJqTkiBTWa
INFO: Shopping list generated: rec... with 15 items
```

## 🐛 Troubleshooting

### Ошибка: "Module not found"

**Решение:**
```bash
# Проверь requirements.txt
# Убедись что pyairtable установлен
pip install pyairtable==2.3.3
```

### Ошибка: "AIRTABLE_API_KEY not set"

**Решение:**
1. Railway → Variables
2. Добавь `AIRTABLE_API_KEY`
3. Redeploy

### Ошибка: "Meal plan not found"

**Решение:**
- Проверь meal_plan_id
- Убедись что план существует в Airtable
- Проверь доступ к базе

### Ошибка: "No planned meals found"

**Решение:**
- Проверь что в плане есть Planned_Meals
- Убедись что Planned_Meals связаны с рецептами

## ✅ Checklist

- [ ] Код закоммичен в GitHub
- [ ] Railway успешно задеплоил
- [ ] Health check работает
- [ ] Swagger UI доступен
- [ ] Shopping List generation работает
- [ ] Items созданы в Airtable
- [ ] n8n workflow подключен
- [ ] n8n workflow протестирован

## 🎯 Next Steps

После успешного деплоя:

1. **Категоризация ингредиентов**
   - Добавить Mercadona sections (Frutas, Carnes, etc.)
   - Группировать items по секциям

2. **Ценовые данные**
   - Добавить Price estimates
   - Калькулировать Total Cost

3. **Telegram интеграция**
   - Отправлять список покупок в Telegram
   - Разрешить отмечать "Purchased" через бота

4. **Batch Cooking Schedule**
   - Генерировать расписание приготовления
   - Оптимизировать по времени

## 📞 Support

Если что-то не работает:
1. Проверь Railway logs
2. Проверь Airtable access
3. Проверь n8n execution logs
