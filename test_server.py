#!/usr/bin/env python3
"""
Скрипт для тестирования Nutrition Server локально
"""
import requests
import json
from datetime import datetime, timedelta

# URL сервера (локально или Railway)
BASE_URL = "http://localhost:8000"  # Измени на Railway URL после деплоя

def test_health():
    """Тест health check"""
    print("🏥 Тестируем health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_create_meal_plan():
    """Тест создания плана питания"""
    print("🍽️ Создаём план питания...")
    
    # Данные для создания плана
    today = datetime.now()
    # Найти ближайший понедельник
    days_until_monday = (7 - today.weekday()) % 7
    next_monday = today + timedelta(days=days_until_monday if days_until_monday != 0 else 7)
    
    data = {
        "user_id": "recw1ls8WIo31cteD",  # ID пользователя Rasta
        "week_start": next_monday.strftime("%Y-%m-%d"),
        "plan_name": f"Test Week {next_monday.strftime('%d %b')}",
        "notes": "Automated test plan"
    }
    
    print(f"Request: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/nutrition/meal-plan/create",
        json=data
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS!")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result["meal_plan_id"]
    else:
        print(f"❌ ERROR!")
        print(f"Response: {response.text}")
        return None

def test_get_meal_plan(plan_id):
    """Тест получения плана питания"""
    if not plan_id:
        print("⏭️ Пропускаем - нет plan_id")
        return
    
    print(f"\n📖 Получаем план питания {plan_id}...")
    response = requests.get(f"{BASE_URL}/api/nutrition/meal-plan/{plan_id}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ План найден!")
        print(f"Всего приёмов пищи: {result['total_meals']}")
    else:
        print(f"❌ Ошибка: {response.text}")

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 ТЕСТИРОВАНИЕ NUTRITION SERVER")
    print("=" * 50)
    print()
    
    # 1. Health check
    test_health()
    
    # 2. Создать план питания
    plan_id = test_create_meal_plan()
    
    # 3. Получить план питания
    test_get_meal_plan(plan_id)
    
    print()
    print("=" * 50)
    print("✅ Тесты завершены!")
    print("=" * 50)
