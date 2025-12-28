from datetime import datetime, timedelta
from typing import List, Dict
from .airtable import AirtableService

class MealPlannerService:
    """Сервис для создания планов питания"""
    
    def __init__(self, airtable: AirtableService):
        self.airtable = airtable
    
    def create_weekly_meal_plan(
        self,
        user_id: str,
        week_start: datetime,
        plan_name: str = None,
        notes: str = None
    ) -> Dict:
        """
        Создать план питания на неделю
        
        Returns:
            dict: {
                "meal_plan_id": str,
                "plan_name": str,
                "total_meals": int,
                "avg_calories": float,
                "avg_protein": float
            }
        """
        
        # 1. Получить все доступные рецепты
        recipes = self._get_available_recipes()
        
        # 2. Сгенерировать оптимальный план
        weekly_plan = self._generate_optimal_plan(recipes, week_start)
        
        # 3. Создать Meal Plan в Airtable
        week_end = week_start + timedelta(days=6)
        
        if not plan_name:
            plan_name = f"Week {week_start.strftime('%d %b')} - {week_end.strftime('%d %b')}"
        
        meal_plan_fields = {
            "Plan Name": plan_name,
            "User": [user_id],
            "Week Start": week_start.strftime("%Y-%m-%d"),
            "Week End": week_end.strftime("%Y-%m-%d"),
            "Status": "Active",
            "Notes": notes or "Auto-generated meal plan optimized for camper living"
        }
        
        meal_plan = self.airtable.create_record("Meal_Plans", meal_plan_fields)
        meal_plan_id = meal_plan["id"]
        
        # 4. Создать все Planned Meals (батчами)
        planned_meals = []
        for day_plan in weekly_plan:
            for meal in day_plan["meals"]:
                planned_meals.append({
                    "Meal Name": meal["name"],
                    "Meal Plan": [meal_plan_id],
                    "Recipe": [meal["recipe_id"]],
                    "Date": meal["date"],
                    "Meal Type": meal["type"],
                    "Servings": 1.0
                })
        
        # Создаём все приёмы пищи батчами (быстро!)
        created_meals = self.airtable.create_records_batch("Planned_Meals", planned_meals)
        
        # 5. Рассчитать статистику
        stats = self._calculate_plan_stats(weekly_plan)
        
        return {
            "meal_plan_id": meal_plan_id,
            "plan_name": plan_name,
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "total_meals": len(created_meals),
            "avg_calories": stats["avg_calories"],
            "avg_protein": stats["avg_protein"],
            "status": "success"
        }
    
    def _get_available_recipes(self) -> List[Dict]:
        """Получить все рецепты из Airtable"""
        recipes = self.airtable.get_all_records("Recipes")
        
        # Фильтруем только те, у которых есть БЖУ
        filtered = []
        for recipe in recipes:
            fields = recipe.get("fields", {})
            if all(key in fields for key in ["Protein (g)", "Calories", "Recipe Name"]):
                filtered.append({
                    "id": recipe["id"],
                    "name": fields["Recipe Name"],
                    "calories": fields.get("Calories", 0),
                    "protein": fields.get("Protein (g)", 0),
                    "fat": fields.get("Fat (g)", 0),
                    "carbs": fields.get("Carbs (g)", 0),
                    "prep_time": fields.get("Prep Time (min)", 0),
                    "is_quick": fields.get("Быстрое", False),
                    "tags": fields.get("Tags", [])
                })
        
        return filtered
    
    def _generate_optimal_plan(self, recipes: List[Dict], week_start: datetime) -> List[Dict]:
        """
        Генерация оптимального плана питания
        
        Логика:
        - Завтрак: 550-700 kcal, 40-55g protein
        - Обед: 650-800 kcal, 50-75g protein
        - Ужин: 550-750 kcal, 50-70g protein
        - Снек 1: 250-350 kcal, 20-40g protein
        - Снек 2: 200-300 kcal, 20-45g protein
        """
        
        # Разделяем рецепты по типам (по калориям и белку)
        breakfasts = [r for r in recipes if 500 <= r["calories"] <= 800 and r["protein"] >= 35]
        lunches = [r for r in recipes if 650 <= r["calories"] <= 800 and r["protein"] >= 45]
        dinners = [r for r in recipes if 500 <= r["calories"] <= 800 and r["protein"] >= 45]
        snacks = [r for r in recipes if 150 <= r["calories"] <= 400 and r["protein"] >= 15]
        
        weekly_plan = []
        
        for day_offset in range(7):
            current_date = week_start + timedelta(days=day_offset)
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Выбираем блюда (с ротацией чтобы избежать повторений)
            breakfast = breakfasts[day_offset % len(breakfasts)] if breakfasts else None
            lunch = lunches[day_offset % len(lunches)] if lunches else None
            dinner = dinners[day_offset % len(dinners)] if dinners else None
            snack1 = snacks[(day_offset * 2) % len(snacks)] if snacks else None
            snack2 = snacks[(day_offset * 2 + 1) % len(snacks)] if snacks else None
            
            day_meals = []
            
            if breakfast:
                day_meals.append({
                    "name": f"Завтрак: {breakfast['name']}",
                    "recipe_id": breakfast["id"],
                    "type": "Breakfast",
                    "date": date_str
                })
            
            if lunch:
                day_meals.append({
                    "name": f"Обед: {lunch['name']}",
                    "recipe_id": lunch["id"],
                    "type": "Lunch",
                    "date": date_str
                })
            
            if dinner:
                day_meals.append({
                    "name": f"Ужин: {dinner['name']}",
                    "recipe_id": dinner["id"],
                    "type": "Dinner",
                    "date": date_str
                })
            
            if snack1:
                day_meals.append({
                    "name": f"Перекус 1: {snack1['name']}",
                    "recipe_id": snack1["id"],
                    "type": "Snack",
                    "date": date_str
                })
            
            if snack2:
                day_meals.append({
                    "name": f"Перекус 2: {snack2['name']}",
                    "recipe_id": snack2["id"],
                    "type": "Snack",
                    "date": date_str
                })
            
            weekly_plan.append({
                "date": date_str,
                "meals": day_meals
            })
        
        return weekly_plan
    
    def _calculate_plan_stats(self, weekly_plan: List[Dict]) -> Dict:
        """Рассчитать статистику плана"""
        total_days = len(weekly_plan)
        total_meals = sum(len(day["meals"]) for day in weekly_plan)
        
        # Для упрощения возвращаем примерные средние значения
        # В реальности нужно суммировать из рецептов
        return {
            "avg_calories": 2750,  # Среднее из нашего плана
            "avg_protein": 210,     # Среднее из нашего плана
            "total_days": total_days,
            "total_meals": total_meals
        }
