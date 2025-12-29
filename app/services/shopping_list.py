"""
Shopping List Generation Service
Генерирует списки покупок на основе планов питания
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pyairtable import Api
import os
from collections import defaultdict


class ShoppingListService:
    def __init__(self):
        self.api = Api(os.getenv('AIRTABLE_API_KEY'))
        self.base_id = 'appBgJb1hzG4vFT1b'
        
        # Table IDs
        self.meal_plans_table = 'tblupjJEeV2Cg4eum'
        self.planned_meals_table = 'tblurMbEfbKrRtGzy'
        self.recipes_table = 'tblgge1WnUvQSnMCh'
        self.recipe_ingredients_table = 'tblfavu2FgY4QesHq'
        self.ingredients_table = 'tblrLuTY8hX8HqEfE'
        self.shopping_lists_table = 'tblw3kjvCpD98webq'
        self.shopping_list_items_table = 'tblnEuDxnpWZ3gEIe'

    def generate_shopping_list(
        self,
        meal_plan_id: str,
        shopping_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Генерирует список покупок для плана питания
        
        Args:
            meal_plan_id: ID плана питания
            shopping_date: Дата покупок (опционально)
            
        Returns:
            Dict с информацией о созданном списке покупок
        """
        # 1. Получаем план питания
        meal_plan = self._get_meal_plan(meal_plan_id)
        if not meal_plan:
            raise ValueError(f"Meal plan {meal_plan_id} not found")
        
        # 2. Получаем все запланированные приёмы пищи
        planned_meals = self._get_planned_meals(meal_plan_id)
        if not planned_meals:
            raise ValueError(f"No planned meals found for meal plan {meal_plan_id}")
        
        # 3. Собираем все рецепты
        recipe_ids = self._extract_recipe_ids(planned_meals)
        
        # 4. Получаем ингредиенты для всех рецептов
        ingredients_data = self._get_ingredients_for_recipes(recipe_ids, planned_meals)
        
        # 5. Агрегируем ингредиенты (группируем одинаковые)
        aggregated_ingredients = self._aggregate_ingredients(ingredients_data)
        
        # 6. Создаём Shopping List
        shopping_list_id = self._create_shopping_list(
            meal_plan_id=meal_plan_id,
            meal_plan=meal_plan,
            shopping_date=shopping_date
        )
        
        # 7. Создаём Shopping List Items (batch)
        items_created = self._create_shopping_list_items(
            shopping_list_id=shopping_list_id,
            ingredients=aggregated_ingredients
        )
        
        return {
            "shopping_list_id": shopping_list_id,
            "meal_plan_id": meal_plan_id,
            "items_count": len(items_created),
            "total_recipes": len(recipe_ids),
            "total_meals": len(planned_meals),
            "items": items_created
        }

    def _get_meal_plan(self, meal_plan_id: str) -> Optional[Dict]:
        """Получает план питания по ID"""
        table = self.api.table(self.base_id, self.meal_plans_table)
        try:
            record = table.get(meal_plan_id)
            return record
        except Exception as e:
            print(f"Error getting meal plan: {e}")
            return None

    def _get_planned_meals(self, meal_plan_id: str) -> List[Dict]:
        """Получает все запланированные приёмы пищи для плана"""
        table = self.api.table(self.base_id, self.planned_meals_table)
        
        # Получаем все records и фильтруем в Python
        # Airtable формулы для linked records работают странно, поэтому фильтруем здесь
        all_records = table.all()
        
        # Фильтруем по meal_plan_id
        filtered_records = []
        for record in all_records:
            meal_plan_links = record['fields'].get('Meal Plan', [])
            if meal_plan_id in meal_plan_links:
                filtered_records.append(record)
        
        return filtered_records

    def _extract_recipe_ids(self, planned_meals: List[Dict]) -> List[str]:
        """Извлекает уникальные ID рецептов из запланированных приёмов"""
        recipe_ids = set()
        for meal in planned_meals:
            recipe = meal['fields'].get('Recipe', [])
            if recipe:
                recipe_ids.update(recipe)
        return list(recipe_ids)

    def _get_ingredients_for_recipes(
        self,
        recipe_ids: List[str],
        planned_meals: List[Dict]
    ) -> List[Dict]:
        """
        Получает ингредиенты для всех рецептов с учётом порций
        
        Returns:
            List of dicts: {
                'ingredient_id': str,
                'ingredient_name': str,
                'quantity': float,
                'unit': str,
                'recipe_name': str
            }
        """
        # Получаем Recipe_Ingredients для всех рецептов
        table = self.api.table(self.base_id, self.recipe_ingredients_table)
        
        # Получаем ВСЕ Recipe_Ingredients и фильтруем в Python
        # (формулы Airtable для linked records работают странно)
        all_recipe_ingredients = table.all()
        
        # Фильтруем только те, которые относятся к нашим рецептам
        recipe_ingredients = []
        recipe_ids_set = set(recipe_ids)
        
        for record in all_recipe_ingredients:
            # Проверяем есть ли recipe_id в поле Recipes 2
            recipes_links = record['fields'].get('Recipes 2', [])
            if any(rid in recipe_ids_set for rid in recipes_links):
                recipe_ingredients.append(record)
        
        # Создаём мапу рецепт -> количество порций
        recipe_servings = {}
        for meal in planned_meals:
            recipe = meal['fields'].get('Recipe', [])
            servings = meal['fields'].get('Servings', 1)
            if recipe:
                for recipe_id in recipe:
                    recipe_servings[recipe_id] = recipe_servings.get(recipe_id, 0) + servings
        
        # Собираем данные об ингредиентах
        ingredients_data = []
        for ri in recipe_ingredients:
            fields = ri['fields']
            
            recipe_id = fields.get('Recipes 2', [None])[0]
            if not recipe_id:
                continue
            
            ingredient = fields.get('Ingredients', [])
            quantity = fields.get('Количество', 0)
            unit = fields.get('Единица измерения')
            
            if not ingredient:
                continue
            
            ingredient_id = ingredient[0]
            
            # Умножаем на количество порций
            total_servings = recipe_servings.get(recipe_id, 1)
            total_quantity = quantity * total_servings
            
            ingredients_data.append({
                'ingredient_id': ingredient_id,
                'quantity': total_quantity,
                'unit': unit,
                'recipe_id': recipe_id
            })
        
        # Получаем названия ингредиентов
        ingredient_ids = list(set([item['ingredient_id'] for item in ingredients_data]))
        ingredients_table = self.api.table(self.base_id, self.ingredients_table)
        
        ingredient_names = {}
        for ing_id in ingredient_ids:
            try:
                ing_record = ingredients_table.get(ing_id)
                ingredient_names[ing_id] = ing_record['fields'].get('Ingredient Name', 'Unknown')
            except:
                ingredient_names[ing_id] = 'Unknown'
        
        # Добавляем названия
        for item in ingredients_data:
            item['ingredient_name'] = ingredient_names.get(item['ingredient_id'], 'Unknown')
        
        return ingredients_data

    def _aggregate_ingredients(self, ingredients_data: List[Dict]) -> List[Dict]:
        """
        Агрегирует ингредиенты (суммирует одинаковые)
        
        Группирует по: ingredient_id + unit
        """
        aggregated = defaultdict(lambda: {'quantity': 0, 'recipes': set()})
        
        for item in ingredients_data:
            key = (item['ingredient_id'], item['unit'])
            aggregated[key]['ingredient_id'] = item['ingredient_id']
            aggregated[key]['ingredient_name'] = item['ingredient_name']
            aggregated[key]['unit'] = item['unit']
            aggregated[key]['quantity'] += item['quantity']
            aggregated[key]['recipes'].add(item.get('recipe_id', ''))
        
        # Конвертируем в список
        result = []
        for key, data in aggregated.items():
            result.append({
                'ingredient_id': data['ingredient_id'],
                'ingredient_name': data['ingredient_name'],
                'quantity': round(data['quantity'], 1),
                'unit': data['unit'],
                'recipe_count': len(data['recipes'])
            })
        
        # Сортируем по названию
        result.sort(key=lambda x: x['ingredient_name'])
        
        return result

    def _create_shopping_list(
        self,
        meal_plan_id: str,
        meal_plan: Dict,
        shopping_date: Optional[str] = None
    ) -> str:
        """Создаёт запись Shopping List"""
        table = self.api.table(self.base_id, self.shopping_lists_table)
        
        # Формируем название
        plan_name = meal_plan['fields'].get('Plan Name', 'Meal Plan')
        week_start = meal_plan['fields'].get('Week Start', '')
        list_name = f"Shopping List - {plan_name} ({week_start})"
        
        # Дата покупок (если не указана - используем Week Start)
        if not shopping_date:
            shopping_date = week_start
        
        # Создаём запись
        record = table.create({
            'List Name': list_name,
            'Meal Plan': [meal_plan_id],
            'Shopping Date': shopping_date,
            'Status': 'Pending'
        })
        
        return record['id']

    def _create_shopping_list_items(
        self,
        shopping_list_id: str,
        ingredients: List[Dict]
    ) -> List[Dict]:
        """Создаёт Shopping List Items (batch)"""
        table = self.api.table(self.base_id, self.shopping_list_items_table)
        
        # Формируем записи для batch create
        records_to_create = []
        for ing in ingredients:
            # Конвертируем единицы из Recipe_Ingredients в Shopping_List_Items
            # Recipe_Ingredients использует "гр", Shopping_List_Items использует "г"
            unit = ing['unit']
            if unit == 'гр':
                unit = 'г'
            
            item_name = f"{ing['ingredient_name']} ({ing['quantity']}{unit})"
            
            record = {
                'Item': item_name,
                'Shopping List': [shopping_list_id],
                'Ingredient': [ing['ingredient_id']],
                'Quantity': ing['quantity'],
                'Unit': unit,
                'Purchased': False
            }
            records_to_create.append(record)
        
        # Batch create (по 10 записей)
        created_records = []
        batch_size = 10
        
        for i in range(0, len(records_to_create), batch_size):
            batch = records_to_create[i:i + batch_size]
            created = table.batch_create(batch)
            created_records.extend(created)
        
        return created_records

    def get_shopping_list(self, shopping_list_id: str) -> Dict[str, Any]:
        """Получает информацию о списке покупок"""
        # Получаем сам список
        list_table = self.api.table(self.base_id, self.shopping_lists_table)
        shopping_list = list_table.get(shopping_list_id)
        
        # Получаем items
        items_table = self.api.table(self.base_id, self.shopping_list_items_table)
        formula = f"{{Shopping List}} = '{shopping_list_id}'"
        items = items_table.all(formula=formula)
        
        return {
            'shopping_list': shopping_list,
            'items': items,
            'items_count': len(items)
        }
