"""
Test script for Shopping List Generation
Тестирует локально без запуска сервера
"""
import os
from dotenv import load_dotenv
from app.services.shopping_list import ShoppingListService

# Загружаем environment variables
load_dotenv()

def test_shopping_list_generation():
    """Тестирует генерацию списка покупок"""
    print("🧪 Testing Shopping List Generation\n")
    
    # Инициализация service
    service = ShoppingListService()
    
    # Meal Plan ID из Airtable
    meal_plan_id = "recnd7GzJqTkiBTWa"  # Test Manual Date plan
    shopping_date = "2024-12-30"
    
    print(f"📋 Generating shopping list for meal plan: {meal_plan_id}")
    print(f"📅 Shopping date: {shopping_date}\n")
    
    try:
        # Генерируем список покупок
        result = service.generate_shopping_list(
            meal_plan_id=meal_plan_id,
            shopping_date=shopping_date
        )
        
        print("✅ Shopping List Generated Successfully!\n")
        print(f"Shopping List ID: {result['shopping_list_id']}")
        print(f"Items Count: {result['items_count']}")
        print(f"Total Recipes: {result['total_recipes']}")
        print(f"Total Meals: {result['total_meals']}\n")
        
        # Получаем детали
        print("📦 Shopping List Items:")
        print("-" * 50)
        
        details = service.get_shopping_list(result['shopping_list_id'])
        for item in details['items']:
            fields = item['fields']
            item_name = fields.get('Item', 'Unknown')
            quantity = fields.get('Quantity', 0)
            unit = fields.get('Unit', '')
            print(f"  • {item_name}")
        
        print("\n" + "=" * 50)
        print(f"🎉 Success! Created {result['items_count']} items")
        print("=" * 50)
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_get_shopping_list():
    """Тестирует получение существующего списка покупок"""
    print("\n🧪 Testing Get Shopping List\n")
    
    service = ShoppingListService()
    
    # Используй существующий shopping_list_id если есть
    shopping_list_id = "rec123456789"  # Замени на реальный ID
    
    try:
        result = service.get_shopping_list(shopping_list_id)
        
        print(f"Shopping List: {result['shopping_list']['fields'].get('List Name')}")
        print(f"Items: {result['items_count']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    # Проверяем API ключ
    api_key = os.getenv('AIRTABLE_API_KEY')
    if not api_key:
        print("❌ AIRTABLE_API_KEY not set!")
        print("Please create .env file with:")
        print("AIRTABLE_API_KEY=pat...")
        exit(1)
    
    print("=" * 50)
    print("  Shopping List Generation Test")
    print("=" * 50)
    print()
    
    # Тест генерации
    result = test_shopping_list_generation()
    
    if result:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
